"""Attribute recorded usage to this audit stream, never to shared-ledger deltas."""


def usage_cost(events):
    events = list(events)
    receipts = {}
    for event in events:
        if event['event_type'] != 'model_usage_received':
            continue
        receipt = event['payload']['receipt']
        identity, cost = receipt['reservation_id'], receipt['accounted_upper_micro_usd']
        if not isinstance(identity, str) or not identity or receipt['state'] != 'settled' or type(cost) is not int or cost < 0:
            raise ValueError('Valid settled usage receipt required')
        if identity in receipts and receipts[identity] != cost:
            raise ValueError('Conflicting receipt cost')
        receipts[identity] = cost
    return {'unique_usage_receipts': len(receipts),
            'accounted_upper_micro_usd': sum(receipts.values()),
            'attempts_without_recorded_usage': sum(
                e.get('payload', {}).get('reservation_id') not in receipts
                for e in events if e['event_type'] == 'model_dispatch_attempted'),
            'basis': 'Unique settled usage receipts in this captured audit; not vendor invoice.',
            'missing_usage_warning': 'Missing usage keeps its reservation; zero settled receipt sum does not mean a free call.',
            'global_snapshot_warning': 'Shared-ledger snapshots may include other concurrent runs or pending reservations.'}
