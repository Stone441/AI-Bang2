"""Source-review dispatch equivalence with no external IO or real budget."""
import json
import unittest
from unittest.mock import patch
from brain.audit import verify_chain
from brain.contracts import Actor
from brain.synthesis import DeepSeekSynthesisModel, DeepSeekReviewedExcerptsModel, DeepSeekCoveredSourceReviewModel
from brain.deepseek import PRICE_DATE, ModelOutputRejected
import test_compact_source_review as compact_tests
import test_source_review as source_tests


class SingleCompact(compact_tests.CompactReview):
    def engine(self):
        engine, world = super().engine()
        engine.source_review_dispatch = 'single'
        return engine, world

    def test_payload_claims_usage_and_full_selected_checks_match_legacy(self):
        answers, payloads, costs = [], [], []
        for mode in ('legacy', 'single'):
            engine, world = self.engine()
            engine.source_review_dispatch = mode
            self.dynamic()
            before = self.ledger.summary()['settled_micro_usd']
            result = engine.query(Actor('eng_b'), 'payment-service incident runbook')
            costs.append(self.ledger.summary()['settled_micro_usd']-before)
            answers.append(result['claims'])
            payloads.append(self.transport.calls[-1])
            events = engine.audit.export()
            checks = [e['payload'] for e in events if e['event_type'] == 'authorization_decided']
            selected = {e['resource_id'] for e in result['evidence']}
            for phase in ('review_dispatch', 'before_dispatch'):
                self.assertEqual({c['resource_id'] for c in checks if c['phase'] == phase}, selected)
            self.assertEqual(bool([c for c in checks if c['phase']=='model_dispatch']), mode=='legacy')
            self.assertIs(verify_chain(events)['valid'], True)
            review_seq = max(e['seq'] for e in events if e['event_type']=='authorization_decided'
                             and e['payload']['phase']=='review_dispatch')
            dispatch_seq = next(e['seq'] for e in events if e['event_type']=='model_dispatch_attempted')
            self.assertLess(review_seq, dispatch_seq)
        self.assertEqual(answers[0], answers[1])
        self.assertEqual(payloads[0], payloads[1])
        self.assertEqual(costs[0], costs[1])

    def test_dual_call_or_unknown_model_cannot_opt_in(self):
        engine, world = self.engine()
        for cls in (DeepSeekSynthesisModel, DeepSeekReviewedExcerptsModel):
            with self.subTest(model=cls.__name__):
                engine.model = cls('synthetic-not-a-key', self.ledger, synthetic_only=True,
                    transport=self.transport, today=PRICE_DATE)
                with self.assertRaisesRegex(ValueError, 'audited source-review model'):
                    engine.query(Actor('eng_b'), 'payment-service incident runbook')
        self.assertEqual(self.transport.calls, [])
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM reservations').fetchone()[0], 0)

    def test_change_after_candidate_check_never_sends_stale_resource(self):
        for outcome in ('deny','unknown','version','deleted'):
            with self.subTest(outcome=outcome):
                engine, world = self.engine()
                self.dynamic()
                self.transport.calls.clear()
                original = engine.checks
                def checked(actor, resources, rid, phase):
                    result = original(actor, resources, rid, phase)
                    if phase == 'before_model':
                        self.change(world, outcome)
                    return result
                with patch.object(engine, 'checks', side_effect=checked):
                    # A changed record may be safely filtered out during selection;
                    # every remaining record must still receive a fresh review check.
                    try:
                        answer = engine.query(Actor('eng_b'), 'payment-service incident runbook')
                    except (PermissionError, ModelOutputRejected):
                        answer = None
                if answer is not None:
                    self.assertNotIn('C-01', {e['resource_id'] for e in answer['evidence']})
                else:
                    self.assertEqual(engine.store.history('eng_b'), [])
                for payload in self.transport.calls:
                    body = json.loads(payload['messages'][1]['content'])
                    self.assertNotIn('C-01@1', {p['evidence_id'] for p in body['passages']})
                if outcome in ('deny', 'unknown'):
                    self.assertEqual(self.transport.calls, [])


class SingleLegacy(source_tests.SourceReview):
    def engine(self):
        engine, world = super().engine()
        engine.source_review_dispatch = 'single'
        return engine, world


class SingleCovered(SingleCompact):
    def candidate(self):
        return DeepSeekCoveredSourceReviewModel('synthetic-not-a-key', self.ledger,
            synthetic_only=True, transport=self.transport, today=PRICE_DATE,
            reasoning_effort='none', output_tokens=8192)
