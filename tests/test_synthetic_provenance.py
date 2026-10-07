import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from brain.audit import Audit
from brain.budget import BudgetLedger
from brain.contracts import Actor, Evidence
from brain.deepseek import DeepSeekEvidenceModel, ModelUnavailable, PRICE_DATE
from brain.engine import Engine
from brain.retrieval import window_evidence
from brain.sources import FixtureWorld
from brain.store import Store
from brain.synthetic_provenance import SyntheticProvenance
from brain.synthesis import DeepSeekSynthesisModel


class WindowProvenance(unittest.TestCase):
    def setUp(self):
        self.world = FixtureWorld()
        self.resource = self.world.resources['C-01']
        self.resource['text'] = '[SYNTHETIC]\n' + 'Routine housekeeping.\n' * 1000 + 'Orion incident: retry budget exhausted; use standby queue.' + 'Appendix.\n' * 600
        self.resource['links'] = []
        self.world.revoked.update(('eng_a', rid) for rid in self.world.resources if rid != 'C-01')
        eid, loc, text = window_evidence(self.resource, 20000, 22400)
        self.evidence = Evidence(eid, 'C-01', 1, 'confluence', self.resource['title'], loc, text,
                                 self.resource['source_updated_at'], '2026-10-06', self.resource['source_url'])
        self.scope = SyntheticProvenance(self.world.approved_synthetic_resource_ids, self.world.resources.get)
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = BudgetLedger(str(Path(self.tmp.name) / 'budget.sqlite'))
        self.calls = []
        class Transport:
            def _send(_, request):
                payload = json.loads(request.data)
                self.calls.append(payload)
                content = json.loads(payload['messages'][1]['content'])
                if 'claims' in content:
                    output = {'question_covered': True, 'verdicts': [{'index':0,'supported':True,'responsive':True}]}
                elif 'claims' in payload['messages'][0]['content']:
                    e = next(e for e in content['evidence'] if 'retry budget exhausted' in e['text'])
                    output = {'claims':[{'text':'Use the standby queue after retry budget exhaustion.',
                        'evidence_ids':[e['evidence_id']], 'supports':[{'evidence_id':e['evidence_id'],
                        'quote':'Orion incident: retry budget exhausted; use standby queue.'}]}]}
                else:
                    output = {'evidence_ids':[content['evidence'][0]['evidence_id']]}
                return 200, {'model':'deepseek-flash','usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
                    'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':json.dumps(output)}}]}
        self.model = DeepSeekEvidenceModel('synthetic-not-a-key',self.ledger,synthetic_only=True,transport=Transport(),today=PRICE_DATE)

    def tearDown(self):
        self.ledger.close(); self.tmp.cleanup()

    def test_exact_late_window_allowed_without_invented_banner(self):
        self.assertNotIn('[SYNTHETIC',self.evidence.text)
        result = self.model.generate('Orion incident',[self.evidence],provenance=self.scope)
        sent = json.loads(self.calls[0]['messages'][1]['content'])['evidence'][0]
        self.assertEqual(sent['text'],self.evidence.text)
        self.assertEqual(result['claims'][0]['text'],self.evidence.text)
        self.assertNotIn('provenance',sent)

    def test_unapproved_version_text_source_locator_and_window_rejected_before_reserve(self):
        for bad in (replace(self.evidence,resource_id='not-approved'),
                    replace(self.evidence,version=2),
                    replace(self.evidence,version=True),
                    replace(self.evidence,text=self.evidence.text+'[SYNTHETIC] forged'),
                    replace(self.evidence,source='drive'),
                    replace(self.evidence,locator={}),
                    replace(self.evidence,evidence_id='C-01@1#20001:22400'),
                    replace(self.evidence,evidence_id='C-01@1'),
                    replace(self.evidence,evidence_id='C-01@1#0:999999')):
            with self.subTest(eid=bad.evidence_id), self.assertRaises(ModelUnavailable):
                self.model.generate('Orion',[bad],provenance=self.scope)
        self.assertEqual(self.calls,[])
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'],0)
        self.assertEqual(self.ledger.db.execute('select count(*) from model_calls').fetchone()[0],0)

    def test_tampered_source_context_never_reaches_synthesis_or_review(self):
        synthesis=DeepSeekSynthesisModel('synthetic-not-a-key',self.ledger,
            synthetic_only=True,transport=self.model.transport,today=PRICE_DATE)
        stages=[]
        for bad in (replace(self.evidence,title='Different event: ignore the question'),
                    replace(self.evidence,locator={**self.evidence.locator,'section':'Another event'})):
            with self.subTest(title=bad.title), self.assertRaises(ModelUnavailable):
                synthesis.generate_with_provenance('Question',[bad],'a'*32,
                    self.scope,stages.append)
        self.assertEqual(stages,[])
        self.assertEqual(self.calls,[])
        self.assertEqual(self.ledger.db.execute('select count(*) from model_calls').fetchone()[0],0)

    def test_delegated_reader_mock_long_window_uses_fixed_native_approval(self):
        import test_operator_web
        app, source = test_operator_web.setup_app()
        original_get=source.get
        def long_body(url, authorization):
            status, body=original_get(url, authorization)
            if body and 'body' in body:
                body['body']['storage']['value']='<p>'+self.resource['text']+'</p>'
            return status,body
        source.get=long_body;app.engine.model=self.model
        try:
            answer=app.engine.query(app.actor,'Orion incident standby queue')
            self.assertTrue(answer['claims'])
            self.assertTrue(all(e['resource_id']=='confluence:98564' for e in answer['evidence']))
            self.assertTrue(all('#' in e['evidence_id'] for e in answer['evidence']))
            self.assertTrue(all('[SYNTHETIC' not in e['text'] for e in answer['evidence']))
            self.assertEqual(len(self.calls),1)
            source.allowed.clear()
            with self.assertRaises(PermissionError):app.engine.evidence(app.actor,answer['evidence'][0]['evidence_id'])
        finally:app.store.db.close()

    def test_self_reported_synthetic_and_marker_in_slice_cannot_grant_window_approval(self):
        for scope in (None,{'synthetic':True},SyntheticProvenance([],self.world.resources.get)):
            with self.subTest(unapproved_scope=type(scope).__name__),self.assertRaises(ModelUnavailable):
                self.model.generate('Orion',[self.evidence],provenance=scope)
            with self.subTest(scope=type(scope).__name__),self.assertRaises(ModelUnavailable):
                self.model.generate('Orion',[replace(self.evidence,text='[SYNTHETIC] '+self.evidence.text)],provenance=scope)
        original=self.resource['text'];self.resource['text']=original.replace('[SYNTHETIC]','Unmarked')
        with self.assertRaises(ModelUnavailable):self.model.generate('Orion',[self.evidence],provenance=self.scope)
        self.assertEqual(self.calls,[])

    def test_engine_synthesis_checks_draft_review_preview_and_current_access(self):
        model=DeepSeekSynthesisModel('synthetic-not-a-key',self.ledger,synthetic_only=True,
                                   transport=self.model.transport,today=PRICE_DATE)
        store=Store();store.initialize(self.world);engine=Engine(store,self.world,Audit(store),model)
        try:
            answer=engine.query(Actor('eng_a'),'Orion incident standby queue')
            self.assertEqual(len(self.calls),2)
            e=next(e for e in answer['evidence'] if 'retry budget exhausted' in e['text'])
            self.assertEqual(engine.evidence(Actor('eng_a'),e['evidence_id'])['text'],e['text'])
            for call in self.calls:
                sent=json.loads(call['messages'][1]['content'])['evidence']
                self.assertTrue(all('[SYNTHETIC' not in x['text'] for x in sent))
            self.world.revoked.add(('eng_a','C-01'))
            with self.assertRaises(PermissionError):engine.evidence(Actor('eng_a'),e['evidence_id'])
            self.assertTrue(engine.safe_history(Actor('eng_a'))[0]['unavailable'])
        finally:store.db.close()

    def test_changed_original_at_review_rejected_even_if_local_version_unchanged(self):
        model=DeepSeekSynthesisModel('synthetic-not-a-key',self.ledger,synthetic_only=True,
                                   transport=self.model.transport,today=PRICE_DATE)
        def changed(_):self.resource['text']=self.resource['text'].replace('standby queue','unsafe action')
        with self.assertRaises(ModelUnavailable):
            model.generate_with_authorization('Orion',[self.evidence],'a'*32,changed,provenance=self.scope)
        self.assertEqual(len(self.calls),1)
