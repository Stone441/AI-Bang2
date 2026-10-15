import copy
import json
from pathlib import Path
import tempfile
import unittest

from brain.audit import Audit
from brain.contracts import Actor
from brain.engine import Engine, FakeExtractiveModel
from brain.retrieval import tokens
from brain.store import Store
from scripts.answer_challenges import load_cases
from scripts.retrieval_challenges import build_world, run


class RetrievalChallenges(unittest.TestCase):
    def setUp(self):
        data,_=load_cases();self.world=build_world(data)
        self.store=Store();self.addCleanup(self.store.db.close)
        self.model=FakeExtractiveModel();self.actor=Actor('eng_a')

    def engine(self):
        self.store.initialize(self.world)
        return Engine(self.store,self.world,Audit(self.store),self.model)

    def test_fixed_questions_and_variants_recall_required_evidence_without_model_api(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'run';report=run(output)
            self.assertEqual(report['queries'],18)
            self.assertEqual(report['missing_evidence_queries'],0)
            self.assertEqual(report['semantic_quality'],'not_evaluated')
            saved=(output/'report.json').read_bytes()
            with self.assertRaises(FileExistsError):run(output)
            self.assertEqual((output/'report.json').read_bytes(),saved)

    def test_glossary_preserves_ids_and_unknown_chinese_does_not_match_everything(self):
        self.assertEqual(tokens('PAY-103完成了吗'),{'pay-103','done','complete'})
        self.assertEqual(tokens('复盘'),tokens('postmortem'))
        self.assertTrue(tokens('支付重试')==tokens('payment-retry'))
        answer=self.engine().query(self.actor,'瓢虫在月球吃馒头')
        self.assertEqual(answer['evidence'],[])
        self.assertEqual(self.model.calls[-1]['evidence'],[])

    def test_chinese_source_matches_english_without_rewriting_evidence_or_preview(self):
        source=self.world.resources['C-02']
        source.update(title='支付重试功能',text='[SYNTHETIC] 支付重试仅支持试点，尚未批准全面开放。')
        original=source['text'];engine=self.engine()
        answer=engine.query(self.actor,'What is payment-retry availability?')
        evidence=next(e for e in answer['evidence'] if e['resource_id']=='C-02')
        self.assertEqual(evidence['text'],original)
        self.assertEqual(engine.evidence(self.actor,evidence['evidence_id'])['text'],original)

    def test_restricted_matching_document_never_enters_model_or_response(self):
        secret=copy.deepcopy(self.world.resources['C-02'])
        secret.update(id='CH-SECRET',text='[SYNTHETIC] 支付重试全面开放 RETRIEVAL_SECRET_CANARY',links=[])
        secret['policy']['page_groups']=['security'];self.world.resources[secret['id']]=secret
        answer=self.engine().query(self.actor,'支付重试现在全面开放了吗？')
        self.assertNotIn('RETRIEVAL_SECRET_CANARY',json.dumps(answer))
        self.assertNotIn('CH-SECRET',{e['resource_id'] for e in self.model.calls[-1]['evidence']})

    def test_revocation_blocks_new_chinese_query_old_history_and_preview(self):
        engine=self.engine();first=engine.query(self.actor,'支付重试全面开放了吗？')
        eid=next(e['evidence_id'] for e in first['evidence'] if e['resource_id']=='C-02')
        self.world.revoked.add(('eng_a','C-02'))
        current=engine.query(self.actor,'支付重试全面开放了吗？')
        self.assertNotIn('C-02',{e['resource_id'] for e in current['evidence']})
        self.assertNotIn('C-02',{e['resource_id'] for e in self.model.calls[-1]['evidence']})
        self.assertTrue(engine.safe_history(self.actor,first['request_id'])[0]['unavailable'])
        with self.assertRaises(PermissionError):engine.evidence(self.actor,eid)

    def test_source_unknown_still_excludes_matching_chinese_evidence(self):
        self.world.faults.add('confluence')
        answer=self.engine().query(self.actor,'支付重试何时全面开放？')
        self.assertNotIn('confluence',{e['source'] for e in answer['evidence']})
        self.assertNotIn('confluence',{e['source'] for e in self.model.calls[-1]['evidence']})
