"""AUTH032 original36 fixture source/live model; distinct from native six."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('quality36',Path(__file__).with_name('quality_v11.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
if __name__=='__main__':
 state=json.loads((ROOT/'.runtime/page-failure-ux-20261008/.runtime/trial-admission.json').read_text())
 assert state['max_attempts']==138 and state['attempts']==99,'Only after fixed six once; no resume/retry'
 module.main(query_expansion='action-terms-v1',output=Path(__file__).with_name('action-ranking-quality36'))
