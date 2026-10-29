import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('transport_review_cli', ROOT / 'scripts/review_cli.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.packet = {'run_id': 'fixture', 'stage': 'review', 'handoff_revision': 0,
                       'target_fingerprint': 'frozen', 'requirements': 'Review only.',
                       'target': {'files': {'example.ts': 'const x = 1;\n'}, 'plan': None,
                                  'diff': '+const x = 1;\n', 'base': 'fixture'}}

    def content(self, size):
        text = 'Fixture instructions\nCURRENT HANDOFF\n' + r.dumps(self.packet) + '\nRESPONSE SCHEMA\n{}\n'
        return text + ' ' * max(0, size - len(text.encode()))

    def prepare(self, content, name='call'):
        call = self.root / name
        call.mkdir()
        r.write_new(call / 'prompt.txt', content)
        return call, r.prepare_transport(content, call)

    def test_threshold_and_unicode_use_utf8_bytes(self):
        for extra, kind in [(0, 'inline'), (1, 'file-bundle')]:
            text = self.content(r.INLINE_BYTES + extra)
            call, wire = self.prepare(text, str(extra))
            self.assertEqual(r.read_json(call/'input-transport.json')['kind'], kind)
            self.assertLessEqual(len(wire.encode()), r.INLINE_BYTES)
        self.packet['requirements'] = '🙂' * 225000
        text = self.content(0)
        self.assertLess(len(text), r.INLINE_BYTES)
        call, _ = self.prepare(text, 'unicode')
        self.assertEqual(r.read_json(call/'input-transport.json')['kind'], 'file-bundle')

    def test_bundle_reconstructs_long_lines_and_crlf_without_escaping_source(self):
        source = ('🙂"\\x' * 5000) + '\r\nlast line without newline'
        self.packet['target']['files']['example.ts'] = source
        text = self.content(r.INLINE_BYTES + 1)
        call, _ = self.prepare(text)
        index = r.read_json(call/'evidence/index.json')
        restored = {}
        for entry in index['sections']:
            value = ''
            for part in entry['parts']:
                display = (call/part['path']).read_bytes().decode()
                page = ''
                cursor = display.index('\n') + 1
                while cursor < len(display):
                    self.assertTrue(display[cursor:].startswith('\nFRAGMENT '))
                    end = display.index('\n', cursor + 1)
                    length = int(display[cursor:end].split(' LENGTH ')[1])
                    self.assertLessEqual(length, 1000)
                    page += display[end + 1:end + 1 + length]
                    cursor = end + 1 + length + 1
                self.assertEqual(r.digest(page.encode()), part['sha256'])
                value += page
            self.assertEqual(r.digest(value.encode()), entry['sha256'])
            restored[entry['section']] = value
        self.assertEqual(restored['Source: example.ts'], source)
        self.assertEqual(restored['Target: diff'], self.packet['target']['diff'])
        self.assertEqual(restored['Instructions'], 'Fixture instructions')
        self.assertIn('RESPONSE SCHEMA', restored['Response instructions'])
        self.assertEqual((call/'prompt.txt').read_bytes(), text.encode())

    def test_modified_missing_and_inaccessible_evidence_block(self):
        text = self.content(r.INLINE_BYTES + 1)
        for number, name in enumerate(['prompt.txt', 'stdin.txt', 'input-transport.json',
                                       'evidence/index.json', 'evidence/0001.txt']):
            with self.subTest(name=name):
                call, _ = self.prepare(text, str(number))
                (call/name).write_text('changed')
                with self.assertRaises(r.ReviewError):
                    r.validate_transport(text, call)
        call, _ = self.prepare(text, 'missing')
        (call/'evidence/0001.txt').unlink()
        with self.assertRaises(r.ReviewError):
            r.validate_transport(text, call)
        call, _ = self.prepare(text, 'denied')
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('fixture')):
            with self.assertRaises(r.ReviewError):
                r.validate_transport(text, call)

    def test_bundle_symlinks_and_oversize_input_fail_before_launch(self):
        text = self.content(r.INLINE_BYTES + 1)
        call, _ = self.prepare(text)
        original = call/'evidence/0001.txt'
        outside = self.root/'outside.txt'
        original.rename(outside)
        original.symlink_to(outside)
        with self.assertRaises(r.ReviewError):
            r.validate_transport(text, call)
        new = self.root/'new'
        new.mkdir()
        (new/'evidence').symlink_to(call/'evidence', target_is_directory=True)
        with self.assertRaises(FileExistsError):
            r.prepare_transport(text, new)
        with patch.object(r.subprocess, 'Popen') as launch:
            r.write_new(new/'agent.json', {'model': 'fixture', 'effort': 'fixture'})
            with self.assertRaises(r.ReviewError):
                r.execute_process(['fixture'], self.root, 'x' * (r.MAX_BYTES + 1), new, 1)
            launch.assert_not_called()

    def test_structured_context_error_and_real_denials_remain_distinct(self):
        envelope = {'is_error': True, 'terminal_reason': 'prompt_too_long',
                    'permission_denials': [], 'api_error_status': 400}
        (self.root/'stdout.log').write_text(json.dumps(envelope))
        (self.root/'stderr.log').write_text('Warning: fixture diagnostic\n')
        self.assertTrue(r.capacity_failure(self.root))
        self.assertTrue(r.capacity_failure(self.root, json.dumps(envelope)))
        for changes in [{'permission_denials': [{'tool': 'Read'}]}, {'is_error': False},
                        {'api_error_status': 403}, {'terminal_reason': 'unknown'},
                        {'permission_denials': None}]:
            with self.subTest(changes=changes):
                self.assertFalse(r.capacity_failure(self.root, json.dumps({**envelope, **changes})))
        (self.root/'stderr.log').write_text('Authentication required')
        self.assertFalse(r.capacity_failure(self.root))
        self.assertFalse(r.capacity_failure(self.root, '{"terminal_reason":"prompt_too_long"'))
        self.assertFalse(r.capacity_failure(self.root, 'input_too_large max_chars=1048576 quota exceeded'))


if __name__ == '__main__':
    unittest.main()
