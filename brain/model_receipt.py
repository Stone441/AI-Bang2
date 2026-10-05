"""Public successful-generation receipt; never infer a call from evidence count."""
import re


def public_receipt(receipt, request_id):
    if not isinstance(receipt, dict):
        raise ValueError('Invalid model receipt')
    if receipt.get('called') is False:
        if receipt != {'called': False, 'reason': 'no_authorized_evidence'}:
            raise ValueError('Invalid no-call receipt')
        return dict(receipt)
    if (receipt.get('called') is not True or receipt.get('query_id') != request_id
            or receipt.get('state') != 'settled' or receipt.get('outcome') != 'accepted'
            or receipt.get('dispatch_recorded') is not True
            or not isinstance(receipt.get('model'), str)
            or not re.fullmatch(r'[a-z0-9-]{1,80}', receipt['model'])
            or not isinstance(receipt.get('reservation_id'), str)
            or not re.fullmatch(r'[0-9a-f]{32}', receipt['reservation_id'])):
        raise ValueError('Invalid completed model receipt')
    counts = [receipt.get(k) for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')]
    costs = [receipt.get(k) for k in ('reserved_micro_usd', 'accounted_upper_micro_usd')]
    if (any(type(v) is not int or v < 0 for v in counts + costs)
            or counts[2] != counts[0] + counts[1]
            or costs[0] <= 0 or costs[1] > costs[0]):
        raise ValueError('Invalid model usage receipt')
    keys = ('query_id', 'model', 'reservation_id', 'prompt_tokens', 'completion_tokens',
            'total_tokens', 'reserved_micro_usd', 'accounted_upper_micro_usd',
            'state', 'outcome', 'called', 'dispatch_recorded')
    return {**{k: receipt[k] for k in keys},
            'accounting_basis': 'conservative peak/cache-miss upper estimate; not vendor invoice'}
