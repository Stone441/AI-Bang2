import unittest
from scripts.run_cost import usage_cost


class CapturedRunCost(unittest.TestCase):
    @staticmethod
    def event(identity, cost, state='settled'):
        return {'event_type': 'model_usage_received', 'payload': {'receipt': {
            'reservation_id': identity, 'accounted_upper_micro_usd': cost, 'state': state}}}

    def test_duplicate_receipts_do_not_double_charge_or_count_pending_reservations(self):
        events = [self.event('first', 23), self.event('first', 23), self.event('second', 11),
                  {'event_type': 'model_dispatch_intent', 'payload': {'reserved_micro_usd': 315802}}]
        result = usage_cost(events)
        self.assertEqual(result['unique_usage_receipts'], 2)
        self.assertEqual(result['accounted_upper_micro_usd'], 34)

    def test_conflicting_or_unsettled_cost_cannot_be_reported_as_actual_usage(self):
        for events in [[self.event('same', 23), self.event('same', 25)],
                       [self.event('pending', 23, 'pending')], [self.event('boolean', True)]]:
            with self.subTest(events=events), self.assertRaises(ValueError):usage_cost(events)

    def test_no_usage_has_zero_cost_even_if_a_request_reserved_budget(self):
        result = usage_cost([{'event_type': 'model_dispatch_attempted'}])
        self.assertEqual(result['accounted_upper_micro_usd'], 0)
        self.assertEqual(result['attempts_without_recorded_usage'], 1)
