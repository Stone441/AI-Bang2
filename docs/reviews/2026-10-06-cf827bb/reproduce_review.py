"""Offline review probes, not a full application or live API/model test.

retrieval_snapshot.py is byte-identical to the pinned repository blob.
The two small guard functions below are transcribed excerpts from brain/deepseek.py.
No credentials, network, model calls, repository writes or user processes are used.
"""
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import retrieval_snapshot as retrieval

PRICE_DATE = date(2026, 10, 5)

def check_price_review(today=None):
    current = today or datetime.now(ZoneInfo('Asia/Singapore')).date()
    if current != PRICE_DATE:
        raise ValueError('Current model price review required')

def marked_synthetic(evidence):
    if '[SYNTHETIC' in evidence.text:
        return True
    # The original approved Atlassian seeds use this exact banner instead of
    # brackets. Accept only their source/fixture pairs, never the title alone.
    lines = {line.strip() for line in evidence.text.splitlines()}
    fixtures = {'confluence': ('C-01', 'C-02'), 'jira': ('J-02', 'J-03')}
    return ('SYNTHETIC COMPETITION TEST DATA — not an actual company record.' in lines
            and any('Fixture ID: ' + fid in lines
                    for fid in fixtures.get(evidence.source, ())))

root = Path(__file__).parent
content = (root / 'retrieval_snapshot.py').read_bytes()
blob = hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
assert blob == 'eeceea5a67c44b6541cd42907137f80a160d4c7e'

resource = {'id':'C-01', 'version':1, 'source':'confluence',
    'title':'Synthetic operations manual', 'locator':{},
    'text': '[SYNTHETIC]\n' + 'Routine housekeeping.\n' * 1000
        + 'Orion incident: retry budget exhausted; early cache explanation withdrawn.\n'
        + 'Appendix.\n' * 600}
queries = [
    'Orion incident retry budget',
    'Orion outage retracted explanation',
    'interruption annulled hypothesis',
    'Which hypothesis was abandoned?',
]
cases = []
for question in queries:
    windows = retrieval.ranked_windows(resource, retrieval.tokens(question))
    cases.append({'question':question, 'query_tokens':sorted(retrieval.tokens(question)),
                  'matched_windows':windows,
                  'target_found':any('retry budget exhausted' in resource['text'][start:end]
                                     for _,start,end in windows)})
_, start, end = retrieval.ranked_windows(resource, retrieval.tokens(queries[0]))[0]
eid, locator, text = retrieval.window_evidence(resource, start, end)
assert 'retry budget exhausted' in text
assert not marked_synthetic(SimpleNamespace(text=text, source='confluence'))

dates = []
for day in (date(2026,10,5), date(2026,10,6), date(2026,10,16)):
    try:
        check_price_review(day)
        dates.append({'date':str(day),'result':'allowed'})
    except ValueError as error:
        dates.append({'date':str(day),'result':'blocked','reason':str(error)})
report = {
    'review_commit':'cf827bb12c022e63f8e1b498c565d79d20ed25e6',
    'mode':'independent_offline_function_probes',
    'retrieval_blob_verified':blob,
    'guard_source':'transcribed pure-function excerpts from brain/deepseek.py at pinned commit',
    'input_origin':'synthetic single-resource text from scripts/retrieval_acceptance.py',
    'date_guard':dates,
    'retrieval_cases':cases,
    'late_window_model_guard': {'evidence_id':eid,'exact_original_slice':True,
          'contains_relevant_fact':True,'marked_synthetic':False,
          'inferred_provider_behavior':'generate rejects nonempty evidence set containing this window before reserve/network'},
    'limits':['Not a full 311-test rerun.',
              'No native platform or model calls; no browser or user-process inspection.',
              'Vocabulary results are a one-document synthetic probe, not a business accuracy rate.',
              'Guard integration consequence follows from static generate() inspection, not a live call.']}
(root/'independent_probes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
