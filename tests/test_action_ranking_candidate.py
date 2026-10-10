"""Disabled-by-default lexical ranking candidate; no semantic/model acceptance claim."""
import unittest
from brain.retrieval import tokens,ranking_terms,subject_related,bm25_windows
from brain.audit import Audit
from brain.engine import Engine
from brain.sources import FixtureWorld
from brain.store import Store


class ActionRanking(unittest.TestCase):
    def test_candidate_prioritizes_operation_without_changing_topic_set(self):
        resources=[
            {'id':'release','title':'Lumen release','text':'Lumen: controlled pilot approved. General release not approved.'},
            {'id':'operation','title':'Lumen operations','text':'Lumen: follow the approved failover procedure.'},
            {'id':'other','title':'Warehouse procedure','text':'Approved procedure: inspect the inventory safeguard.'}]
        query=tokens('What is the latest approved mitigation for Lumen?')
        visible=subject_related(resources,query)
        self.assertNotIn('other',{r['id'] for r in visible})
        scores=bm25_windows(visible,ranking_terms(query,'action-terms-v1'))
        ranked=sorted(visible,key=lambda r:-scores.get(r['id'],[(0,0,0)])[0][0])
        self.assertEqual(ranked[0]['id'],'operation')
        self.assertEqual({r['id'] for r in ranked},{'release','operation'})
        self.assertEqual(query,tokens('What is the latest approved mitigation for Lumen?'))

    def test_default_and_unrelated_questions_are_unchanged(self):
        for question in ('Which code fix is complete?', 'What is the retry policy?', 'Who approved the pilot?'):
            query=tokens(question)
            self.assertEqual(ranking_terms(query,'action-terms-v1'),query)
        query=tokens('What is the mitigation for Lumen?')
        self.assertEqual(ranking_terms(query),query)
        with self.assertRaises(ValueError):ranking_terms(query,'unapproved-strategy')
        store=Store()
        try:
            world=FixtureWorld();store.initialize(world);engine=Engine(store,world,Audit(store))
            self.assertEqual(engine.query_expansion,'none')
            with self.assertRaises(ValueError):Engine(store,world,Audit(store),query_expansion='unapproved-strategy')
        finally:store.db.close()
