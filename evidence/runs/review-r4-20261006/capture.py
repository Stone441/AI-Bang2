"""Offline current-module capture using the tested fixture/mock harness."""
import json
from pathlib import Path
from test_model_stages import ModelStages

for case in ('success','guard','price','budget','timeout','review'):
    target=Path(__file__).parent/(case+'-actual.json')
    if target.exists():raise SystemExit('Refuse evidence overwrite: '+str(target))
    harness=ModelStages();harness.setUp()
    try:result=harness.run_case(case)
    finally:harness.tearDown()
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(case,result['transport_calls'],result['error_type'])
