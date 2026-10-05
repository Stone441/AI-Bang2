import copy
import json
import unittest

from brain.audit import Audit, verify_chain
from brain.contracts import Actor, Evidence
from brain.deepseek import marked_synthetic
from brain.engine import Engine, FakeExtractiveModel
from brain.retrieval import ranked_windows, spans, tokens
from brain.sources import FixtureWorld
from brain.store import Store


class RetrievalWindows(unittest.TestCase):
    def setUp(self):
        self.world = FixtureWorld()
        # Relevant content appears after the old entire-document budget.
        r = self.world.resources['C-01']
        r['title'] = 'Synthetic long operations manual'
        r['text'] = '[SYNTHETIC]\n' + ('Routine housekeeping.\n' * 1000) + '\nOrion incident: retry budget exhausted; use standby queue.\n' + ('Appendix.\n' * 600)
        r['links'] = []
        self.store = Store(); self.store.initialize(self.world)
        self.model = FakeExtractiveModel()
        self.audit = Audit(self.store)
        self.engine = Engine(self.store, self.world, self.audit, self.model)
        self.actor = Actor('eng_a')

    def tearDown(self): self.store.db.close()

    def ask(self): return self.engine.query(self.actor, 'Orion outage standby queue')

    def test_late_relevant_content_and_exact_preview(self):
        answer = self.ask()
        selected = [e for e in answer['evidence'] if e['resource_id'] == 'C-01']
        self.assertTrue(selected)
        self.assertTrue(any('retry budget exhausted' in e['text'] for e in selected))
        original = self.world.resources['C-01']['text']
        for e in selected:
            w = e['locator']['text_window']
            self.assertEqual(e['text'], original[w['start']:w['end']])
            self.assertEqual(self.engine.evidence(self.actor, e['evidence_id'])['text'], e['text'])
        self.assertLessEqual(sum(len(e['text']) for e in answer['evidence']), 16000)
        self.assertTrue(verify_chain(self.audit.export())['valid'])

    def test_revoke_old_windows_history_and_followup(self):
        answer = self.ask()
        eid = next(e['evidence_id'] for e in answer['evidence'] if e['resource_id'] == 'C-01')
        self.world.mutate('C-01', 'revoke', user_id='eng_a')
        with self.assertRaises(PermissionError): self.engine.evidence(self.actor, eid)
        self.assertTrue(self.engine.safe_history(self.actor, answer['request_id'])[0]['unavailable'])
        self.engine.query(self.actor, 'Repeat Orion details', answer['request_id'])
        self.assertNotIn('C-01', {e['resource_id'] for e in self.model.calls[-1]['evidence']})

    def test_changed_version_and_deletion_block_old_windows(self):
        for kind in ('content', 'delete'):
            with self.subTest(kind=kind):
                answer = self.ask()
                eid = next(e['evidence_id'] for e in answer['evidence'] if e['resource_id'] == 'C-01')
                original = copy.deepcopy(self.world.resources['C-01'])
                self.world.mutate('C-01', kind, version=2)
                with self.assertRaises(PermissionError): self.engine.evidence(self.actor, eid)
                self.assertTrue(self.engine.safe_history(self.actor, answer['request_id'])[0]['unavailable'])
                self.ask()
                self.assertNotIn('C-01', {e['resource_id'] for e in self.model.calls[-1]['evidence']})
                self.world.resources['C-01'] = original

    def test_noncanonical_slices_and_legacy_long_id_rejected(self):
        for eid in ('C-01@1', 'C-01@1#1:2401', 'C-01@1#0:99999', 'C-01@1#-1:4', 'C-01@01#0:2400', 'C-01@1#0:2400#x'):
            with self.subTest(eid=eid), self.assertRaises(PermissionError):
                self.engine.evidence(self.actor, eid)

    def test_unknown_never_sends_windows_to_model(self):
        self.world.faults.add('confluence')
        self.ask()
        self.assertNotIn('C-01', {e['resource_id'] for e in self.model.calls[-1]['evidence']})

    def test_revoke_before_dispatch_does_not_persist_answer(self):
        self.engine.before_dispatch = lambda: self.world.mutate('C-01', 'revoke', user_id='eng_a')
        with self.assertRaises(PermissionError): self.ask()
        self.assertEqual(self.store.history('eng_a'), [])

    def test_restricted_resource_not_merged_into_public_windows(self):
        self.world.resources['C-03']['text'] = '[SYNTHETIC] Orion SECRET_NEIGHBOR'
        # Reinitialize after creating the restricted content, so it exists in the index.
        self.store.db.close(); self.store = Store(); self.store.initialize(self.world)
        self.engine = Engine(self.store, self.world, Audit(self.store), self.model)
        answer = self.ask()
        self.assertNotIn('SECRET_NEIGHBOR', json.dumps(answer))
        self.assertNotIn('C-03', {e['resource_id'] for e in self.model.calls[-1]['evidence']})

    def test_marker_is_not_invented_for_real_model_windows(self):
        answer = self.ask()
        late = next(e for e in answer['evidence'] if 'retry budget exhausted' in e['text'])
        self.assertFalse(marked_synthetic(Evidence(**late)))
        self.assertNotIn('[SYNTHETIC]', late['text'])

    def test_aliases_and_unrelated_question(self):
        self.assertEqual(tokens('outages retracted remediation'), tokens('incident withdrawn fix'))
        self.assertEqual(self.engine.query(self.actor, 'unfindablezebra')['evidence'], [])

    def test_window_boundaries_and_limits(self):
        for length in (0, 3999, 4000, 4001, 6400, 30000):
            text = '界' * length
            ss = spans(text)
            self.assertEqual(ss[0][0], 0); self.assertEqual(ss[-1][1], length)
            self.assertTrue(all(start < end for start, end in ss) or length == 0)
            self.assertTrue(all(ss[i][1] >= ss[i+1][0] for i in range(len(ss)-1)))
        r = self.world.resources['C-01']
        self.assertLessEqual(len(ranked_windows(r, tokens('housekeeping'))), 3)
