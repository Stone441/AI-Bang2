"""AUTH032 fixed original native six via49161; no automatic paid retry."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
path=Path(__file__).with_name('http_v11.py')
spec=importlib.util.spec_from_file_location('native_six',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
if __name__=='__main__':
 state=json.loads((ROOT/'.runtime/page-failure-ux-20261008/.runtime/trial-admission.json').read_text())
 assert state['max_attempts']==138 and state['attempts']==93,'AUTH032 schedule starts once at93; no resume/retry'
 module.OUTPUT=Path(__file__).with_name('action-ranking-native-six')
 module.main(private_ticket=ROOT/'.runtime/page-failure-ux-logs/human-bootstrap-token',query_expansion='action-terms-v1')
