import unittest
from brain.audit import Audit
from brain.confluence import SourceUnavailable
from brain.contracts import Actor
from brain.engine import Engine,FakeExtractiveModel
from brain.sources import FixtureWorld
from brain.store import Store
from test_container_discovery import setup

class SourceFaultCompleteness(unittest.TestCase):
    def test_fixture_unknown_stops_synthesis_without_model_or_answer(self):
        world=FixtureWorld();world.faults.add('drive');store=Store();self.addCleanup(store.db.close)
        store.initialize(world);audit=Audit(store);model=FakeExtractiveModel();model.claim_format='grounded_synthesis_v1'
        engine=Engine(store,world,audit,model)
        with self.assertRaises(SourceUnavailable):engine.query(Actor('eng_a'),'payment-service incident')
        self.assertEqual(model.calls,[]);self.assertEqual(store.history('eng_a'),[])
        self.assertFalse(any(e['event_type']=='model_dispatch_attempted' for e in audit.export()))

    def test_legacy_prepare_unknown_is_not_complete_empty_synthesis(self):
        store,pilot,http,_=setup();self.addCleanup(store.db.close)
        model=FakeExtractiveModel();model.claim_format='grounded_synthesis_v1';pilot.engine.model=model
        http['drive'].identity_ok=False
        with self.assertRaises(SourceUnavailable):pilot.query(Actor('eng_b','pilot'),'unfindable')
        self.assertEqual(model.calls,[]);self.assertEqual(store.history('eng_b'),[])

    def test_fake_empty_diagnostic_reports_incomplete_without_source_details(self):
        world=FixtureWorld();world.faults.add('drive');store=Store();self.addCleanup(store.db.close)
        store.initialize(world);engine=Engine(store,world,Audit(store))
        # An unrelated query has no indexed match and no source check; it does not prove source health.
        engine.query(Actor('eng_a'),'unfindable')
        result=engine.query(Actor('eng_a'),'payment-service incident')
        self.assertTrue(result['claims'])
        notice=' '.join(result['uncertainties'])
        self.assertIn('may omit relevant information',notice)
        self.assertNotIn('drive',notice.lower());self.assertNotIn('D-01',notice)

    def test_internal_unknown_lookup_is_actor_and_request_scoped(self):
        store=Store();self.addCleanup(store.db.close);audit=Audit(store)
        audit.append('authorization_decided','eng_a','old',{'result':'unknown'})
        self.assertTrue(audit.request_has_unknown('eng_a','old'))
        self.assertFalse(audit.request_has_unknown('eng_b','old'))
        self.assertFalse(audit.request_has_unknown('eng_a','new'))
        self.assertFalse(audit.request_has_unknown('eng_a',"old' OR 1=1--"))

if __name__=='__main__':unittest.main()
