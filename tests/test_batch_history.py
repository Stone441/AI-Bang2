"""Current History authorization equivalence, including immutable windows."""
import copy
from unittest.mock import patch
from brain.contracts import Actor
from brain.retrieval import spans, window_evidence
import test_source_review as source_tests
import test_source_review_dispatch_contract as dispatch_tests


class BatchHistory(source_tests.SourceReview):
    def engine(self):
        engine, world = super().engine()
        engine.history_read_mode = 'batch'
        return engine, world

    def test_every_history_access_checks_full_set_again_and_matches_serial(self):
        engine, world = self.engine(); self.dynamic_review()
        actor = Actor('eng_b')
        answer = engine.query(actor, 'payment-service incident runbook')
        checked = engine.checks
        calls = []
        def checks(actor, resources, rid, phase):
            calls.append((phase, [r['id'] for r in resources]))
            return checked(actor, resources, rid, phase)
        with patch.object(engine, 'checks', side_effect=checks):
            self.assertEqual(engine.safe_history(actor, answer['request_id']), [answer])
            self.assertEqual(engine.safe_history(actor, answer['request_id']), [answer])
        expected = list(dict.fromkeys(e['resource_id'] for e in answer['evidence']))
        self.assertEqual(calls, [('history', expected)]*2)
        engine.history_read_mode = 'serial'
        self.assertEqual(engine.safe_history(actor, answer['request_id']), [answer])
        self.assertEqual(len(self.transport.calls), 1)

    def test_changed_permission_unknown_version_or_delete_returns_only_unavailable(self):
        for outcome in ('deny','unknown','version','deleted'):
            with self.subTest(outcome=outcome):
                engine, world = self.engine(); self.dynamic_review()
                answer = engine.query(Actor('eng_b'), 'payment-service incident runbook')
                dispatch_tests.DispatchContract.change(world, outcome)
                result = engine.safe_history(Actor('eng_b'), answer['request_id'])[0]
                self.assertTrue(result['unavailable'])
                self.assertEqual(set(result), {'request_id','unavailable','message'})

    def test_forged_window_or_claim_never_returns_saved_answer(self):
        engine, world = self.engine(); self.dynamic_review()
        actor = Actor('eng_b'); answer = engine.query(actor, 'payment-service incident runbook')
        bad_window = copy.deepcopy(answer)
        bad_window['evidence'][0]['evidence_id'] += '#1:20'
        bad_quote = copy.deepcopy(answer)
        bad_quote['claims'][0]['supports'][0]['quote'] = 'Invented source content'
        for corrupted in (bad_window, bad_quote):
            with patch.object(engine.store, 'run', return_value=corrupted):
                result = engine.safe_history(actor, answer['request_id'])[0]
                self.assertEqual(set(result), {'request_id','unavailable','message'})
                self.assertTrue(result['unavailable'])

    def test_multiple_windows_have_one_fresh_resource_check(self):
        engine, world = self.engine()
        resource = copy.deepcopy(engine.store.get('C-01'))
        resource['text'] = '[SYNTHETIC] ' + ('Archive qualification. '*300)
        world.resources['C-01'] = resource
        windows = [window_evidence(resource, start, end) for start,end in spans(resource['text'])[:3]]
        old_get = engine.store.get
        with patch.object(engine.store, 'get', side_effect=lambda rid: resource if rid=='C-01' else old_get(rid)), \
             patch.object(engine, 'checks', wraps=engine.checks) as checks:
            current = engine.current_history_evidence(Actor('eng_b'),
                [{'evidence_id':eid} for eid,_,_ in windows], 'historical-request')
        self.assertEqual(len(checks.call_args.args[1]), 1)
        self.assertEqual([e['text'] for e in current], [text for _,_,text in windows])
