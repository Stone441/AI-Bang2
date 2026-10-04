"""Run unittest and persist actual results including failures, source hashes and commit."""
import hashlib
import json
import platform
import subprocess
import sys
import unittest
from pathlib import Path
from scripts.build_metadata import revision,dirty
from brain.contracts import now

class RecordingResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.cases=[]
    def addSuccess(self,test):super().addSuccess(test);self.cases.append({'test':test.id(),'status':'passed'})
    def addFailure(self,test,err):super().addFailure(test,err);self.cases.append({'test':test.id(),'status':'failed'})
    def addError(self,test,err):super().addError(test,err);self.cases.append({'test':test.id(),'status':'error'})

if __name__=='__main__':
    started=now();suite=unittest.defaultTestLoader.discover('tests')
    result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(suite)
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for root in ['brain','tests','fixtures','scripts','web','tools'] for p in Path(root).rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    for case in result.cases:
        case['mode']='mock_http_contract' if case['test'].startswith(('test_confluence.','test_confluence_probe.','test_confluence_query.','test_confluence_revocation.','test_jira.','test_delegated_query.','test_operator_web.','test_jira_query.')) else 'local_synthetic'
    report={'started_at':started,'finished_at':now(),'mode':'local_synthetic_and_mock_http','live_api_called':False,'python':platform.python_version(),'commit':revision(),'source_hashes':hashes,'tests_run':result.testsRun,'successful':result.wasSuccessful(),'results':result.cases,'failures':[str(x) for x in result.failures],'errors':[str(x) for x in result.errors]}
    path=Path('evidence/runs/local-latest');path.mkdir(parents=True,exist_ok=True)
    (path/'tests.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(not result.wasSuccessful())
