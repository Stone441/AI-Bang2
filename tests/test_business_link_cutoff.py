"""Weak matching targets below the lexical cutoff still follow source-authored links."""
import copy
import unittest
from brain.audit import Audit
from brain.contracts import Actor
from brain.engine import Engine
from brain.sources import FixtureWorld
from brain.store import Store

class LinkCandidateCutoff(unittest.TestCase):
    def setUp(self):
        self.world=FixtureWorld()
        for i in range(40):
            r=copy.deepcopy(self.world.resources['J-03']);rid='DECOY-'+str(i)
            r.update(id=rid,title='Catalog status owner '+str(i),text='Catalog status owner code '+str(i),links=[])
            self.world.resources[rid]=r
        self.store=Store();self.store.initialize(self.world);self.addCleanup(self.store.db.close)
        self.audit=Audit(self.store);self.engine=Engine(self.store,self.world,self.audit)
        self.actor=Actor('eng_a');self.question='payment-service safeguard status owner'

    def test_weak_matching_target_is_expanded_and_retains_original_text(self):
        answer=self.engine.query(self.actor,self.question)
        target=next(e for e in answer['evidence'] if e['resource_id']=='J-03')
        self.assertEqual(target['text'],self.world.resources['J-03']['text'])
        events=[e for e in self.audit.export() if e['request_id']==answer['request_id']]
        self.assertTrue(any(e['payload'].get('resource_id')=='D-01' and e['payload'].get('phase')=='link_seed' and e['payload']['result']=='allow' for e in events))
        self.assertTrue({'before_model','model_dispatch','before_dispatch'}<={e['payload'].get('phase') for e in events if e['payload'].get('resource_id')=='J-03'})
        self.assertLessEqual(len(answer['evidence']),24)

    def test_current_seed_denial_cannot_expand_its_links(self):
        self.world.mutate('D-01','revoke',user_id='eng_a')
        answer=self.engine.query(self.actor,self.question)
        self.assertNotIn('J-03',{e['resource_id'] for e in answer['evidence']})

    def test_current_target_denial_cannot_be_bypassed_by_link(self):
        self.world.mutate('J-03','revoke',user_id='eng_a')
        answer=self.engine.query(self.actor,self.question)
        self.assertNotIn('J-03',{e['resource_id'] for e in answer['evidence']})
        self.assertNotIn('J-03',{e['resource_id'] for e in self.engine.model.calls[-1]['evidence']})

if __name__=='__main__':unittest.main()
