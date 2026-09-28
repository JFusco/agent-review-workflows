#!/usr/bin/env python3
"""Create credential-free disposable fixtures; never call models or touch existing projects."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('review_cli', ROOT/'scripts/review_cli.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
trial=Path(tempfile.mkdtemp(prefix='agent-review-trial-')).resolve()
results={'trial':str(trial),'runs':{}}
for mode, plan in [('implementation',None),('plan','overcomplicated-plan.md')]:
    project=trial/mode; project.mkdir()
    for name in ('calculator.py','test_calculator.py'):
        shutil.copy2(ROOT/'tests/fixtures'/name,project/name)
    (project/'.gitignore').write_text('__pycache__/\n')
    subprocess.run(['git','init','-q',str(project)],check=True)
    subprocess.run(['git','-C',str(project),'add','.'],check=True)
    subprocess.run(['git','-C',str(project),'-c','user.name=Review fixture','-c','user.email=fixture@example.invalid','-c','core.hooksPath=/dev/null','commit','-qm','Disposable fixture'],check=True)
    args=argparse.Namespace(project=str(project),mode=mode,scope=['calculator.py','test_calculator.py'],
        requirements=str(ROOT/'tests/fixtures/requirements.md'), plan=str(ROOT/'tests/fixtures'/plan) if plan else None,
        runs_dir=str(trial/'runs'),base='HEAD',timeout=900,check=['python3 -m unittest -v'] if mode=='implementation' else [])
    run,state=r.initialize(args)
    results['runs'][mode]=str(run)
(trial/'trial.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
