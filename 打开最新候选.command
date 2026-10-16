#!/usr/bin/env python3
"""Open the verified current candidate; never silently route to the old UI."""
import subprocess,sys
from pathlib import Path
candidate=Path(__file__).resolve().parent.parent/'AI-Bang2-semantic-20261015'
control=candidate/'.runtime/human-latest-20261016/entry.json'
command=[sys.executable,str(candidate/'scripts/candidate_entry.py'),'--control',str(control)]
if '--check' in sys.argv or '--refresh-only' in sys.argv:command.append('--check')
try:
    subprocess.run(command,check=True)
except Exception:
    print('最新候选暂不可用；没有回退到旧页面。请让我检查最新试用服务。')
    if '--check' not in sys.argv and '--refresh-only' not in sys.argv:input('按回车关闭窗口。')
    sys.exit(1)
