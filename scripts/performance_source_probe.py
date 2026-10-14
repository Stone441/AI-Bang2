"""AUTH036: four bounded Confluence reads, no model, body logging or source writes."""
import json
import time
from unittest.mock import patch
import http.client

from brain.confluence import Delegation
from brain.contracts import Actor
from brain.http_pool import PooledOpener
from brain.keychain import MacKeychain
from scripts.confluence_probe import load_reader
from scripts.performance_trial import ROOT, PRIVATE, private_directory, write_private


class Counted:
    def __init__(self, delegate):
        self.delegate, self.count = delegate, 0

    def open(self, *args, **kwargs):
        self.count += 1
        return self.delegate.open(*args, **kwargs)


def main():
    private_directory(PRIVATE)
    target = PRIVATE/'confluence-transport-probe-v2.json'
    if target.exists():
        raise ValueError('Existing native probe must not be overwritten or automatically repeated')
    result = {'mode': 'native_api_read_only_no_model', 'source': 'confluence',
              'model_calls': 0, 'samples': [], 'complete_answer_benchmark': False}
    pool = None
    try:
        bundle_path = ROOT/'.runtime/operator-bundle.json'
        bundle = json.loads(bundle_path.read_text())
        if bundle.get('approved_synthetic_only') is not True or bundle.get('identity_mapping_reviewed') is not True:
            raise ValueError('Approved mapping required')
        path = bundle_path.parent/bundle['sources']['confluence']
        config = json.loads(path.read_text())
        reader = load_reader(path)
        account = config['delegations']['eng_b']['account_id']
        credential = MacKeychain().get('confluence', reader.tenant, 'eng_b', account)
        if credential is None:
            raise ValueError('Existing app-owned credential required')
        reader.delegations['eng_b'] = Delegation(account, credential)
        actor = Actor('eng_b', reader.tenant)
        page = sorted(reader.page_ids)[0]
        original = reader.transport.opener
        pool = PooledOpener(reader.api_base, original)
        baseline = None
        original_init = http.client.HTTPSConnection.__init__
        for label, opener in [('legacy_first', original), ('pooled_cold', pool),
                              ('pooled_warm', pool), ('legacy_last', original)]:
            counted = Counted(opener)
            reader.transport.opener = counted
            connections = []
            def counted_init(connection, *args, **kwargs):
                connections.append(1)
                return original_init(connection, *args, **kwargs)
            # Keep the class object intact: stdlib __init__ uses explicit super.
            with patch.object(http.client.HTTPSConnection, '__init__', counted_init):
                started = time.perf_counter()
                decision, content = reader.read(actor, page)
                seconds = time.perf_counter()-started
            if baseline is None and content is not None:
                baseline = content
            result['samples'].append({'configuration': label, 'seconds': seconds,
                'decision': decision.result, 'http_requests': counted.count,
                'https_connection_objects': len(connections),
                'same_content_as_first': content is not None and content == baseline})
            # No retries, no lesser successful evidence set after a source failure.
            if decision.result != 'allow' or content is None:
                result['status'] = 'source_unavailable'
                break
        else:
            result['status'] = 'completed'
    except Exception as error:
        result['status'] = 'stopped'
        result['error_category'] = type(error).__name__
    finally:
        if pool is not None:
            pool.close()
        write_private(target, json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result.get('status') == 'completed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
