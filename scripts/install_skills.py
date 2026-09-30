#!/usr/bin/env python3
"""Install idempotent global skill symlinks without replacing unrelated content."""
import argparse
import json
import os
import shutil
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--skills-dir',type=Path,default=Path.home()/'.agents/skills')
parser.add_argument('--codex-bin',help='Record an explicit Codex executable for this installation only.')
args=parser.parse_args()
destination=args.skills_dir.expanduser()
pairs=[(root/'skills'/name,destination/name) for name in ('review-plan','review-implementation','review-handoff')]
codex_binary = shutil.which(os.path.expanduser(args.codex_bin)) if args.codex_bin else None
if args.codex_bin and not codex_binary:
    parser.error(f'Codex executable is unavailable: {args.codex_bin}')
# Preflight every link before changing any of them.
for source,link in pairs:
    if not (source/'SKILL.md').is_file():
        parser.error(f'Missing skill source: {source}')
    if link.exists() or link.is_symlink():
        if not link.is_symlink() or link.resolve()!=source.resolve():
            parser.error(f'Refusing to replace existing content: {link}')
destination.mkdir(parents=True,exist_ok=True)
for source,link in pairs:
    if not link.is_symlink():
        link.symlink_to(source.resolve(),target_is_directory=True)
    print(f'{link} -> {source.resolve()}')
if codex_binary:
    config_path = root/'runtime.local.json'
    try:
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
    except (OSError, ValueError) as exc:
        parser.error(f'Cannot read {config_path}: {exc}')
    if not isinstance(config, dict):
        parser.error(f'{config_path} must contain a JSON object')
    config['codex_binary'] = str(Path(codex_binary).resolve())
    temporary = config_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(config,indent=2)+'\n')
    temporary.chmod(0o600)
    temporary.replace(config_path)
    print(f'Installation Codex executable: {config["codex_binary"]}')
