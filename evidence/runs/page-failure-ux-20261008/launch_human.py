"""AUTH031 same49161 human continuation, remaining3 questions only.

Store one-time token privately, never a full bootstrap URL in logs/evidence.
No new scope, source write, model configuration or budget counter reset.
"""
import importlib.util,sys,os
from pathlib import Path
from brain import operator_web
ROOT=Path(__file__).resolve().parents[3]
private=ROOT/'.runtime/page-failure-ux-logs'
spec=importlib.util.spec_from_file_location('bounded_trial',Path(__file__).with_name('launch.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class SafeOutput:
 def write(self,value):
  if '#ticket=' in value:
   import re
   token=re.search(r'#ticket=([A-Za-z0-9_-]+)',value).group(1)
   p=private/'human-bootstrap-token';p.write_text(token);p.chmod(0o600)
   value='One-time token stored privately; use the human-entry instructions.'
  return sys.__stdout__.write(value)
 def flush(self):return sys.__stdout__.flush()
if __name__=='__main__':
 sys.stdout=SafeOutput()
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument("--query-expansion",choices=("none","action-terms-v1"),default="none")
 args=parser.parse_args()
 raise SystemExit(module.main(query_expansion=args.query_expansion))
