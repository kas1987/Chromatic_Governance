#!/usr/bin/env bash
set -euo pipefail
root="${1:-.}"
python3 - "$root" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
fail = 0
for plugin in sorted([p for p in root.iterdir() if p.is_dir() and p.name != 'scripts']):
    name = plugin.name
    manifest = plugin/'.claude-plugin'/'plugin.json'
    if not manifest.is_file():
        print(f'FAIL {name} missing manifest')
        fail = 1
        continue
    try:
        json.loads(manifest.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'FAIL {name} invalid manifest: {exc}')
        fail = 1
    if not (plugin/'README.md').is_file():
        print(f'FAIL {name} missing README')
        fail = 1
    skills = plugin/'skills'
    if skills.is_dir():
        for skill_dir in sorted([p for p in skills.iterdir() if p.is_dir()]):
            if not (skill_dir/'SKILL.md').is_file():
                print(f'FAIL {name} skill missing SKILL.md: {skill_dir}')
                fail = 1
    print(f'OK {name}')
sys.exit(fail)
PY
