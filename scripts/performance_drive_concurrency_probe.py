"""AUTH036: bounded approved Drive reads, no model, consent or source writes."""
from concurrent.futures import ThreadPoolExecutor
import json
import threading
import time
from brain.contracts import Actor
from brain.drive_oauth import load_client, refresh_access, verify_account
from brain.http_pool import PooledOpener
from brain.keychain import MacKeychain
from scripts.drive_query import prepare_oauth_reader
from scripts.performance_trial import ROOT, PRIVATE, private_directory, write_private


class Counted:
    def __init__(self, delegate):
        self.delegate, self.count, self.lock = delegate, 0, threading.Lock()

    def open(self, *args, **kwargs):
        with self.lock:
            self.count += 1
        return self.delegate.open(*args, **kwargs)


def main():
    private_directory(PRIVATE)
    target = PRIVATE/'drive-concurrency-probe-v1.json'
    if target.exists(): raise ValueError('Existing probe must not be repeated or overwritten')
    result = {'mode': 'native_api_read_only_no_model', 'model_calls': 0,
              'complete_answer_benchmark': False, 'samples': []}
    pools = {}
    try:
        bundle_path = ROOT/'.runtime/operator-bundle.json'
        bundle = json.loads(bundle_path.read_text())
        if bundle.get('approved_synthetic_only') is not True or bundle.get('identity_mapping_reviewed') is not True:
            raise ValueError('Approved mapping required')
        reader, config = prepare_oauth_reader(bundle_path.parent/bundle['sources']['drive'], 'eng_b')
        client = load_client(ROOT/'.runtime/drive-oauth-client.json', config['oauth_client_id'])
        email = config['oauth_operator']['email']
        refresh = MacKeychain().get('drive', reader.tenant, 'eng_b', client.client_id+'|'+email.casefold())
        if refresh is None: raise ValueError('Existing authorization required')
        # Existing grant refresh only. No authorize(), hidden input or persistence.
        reader.delegations['eng_b'] = verify_account(refresh_access(client, refresh), email, reader.transport)
        del refresh
        actor = Actor('eng_b', reader.tenant)
        native_ids = sorted(reader.native_ids)
        if not 3 <= len(native_ids) <= 4: raise ValueError('Bounded three or four mapped files required')
        original = reader.transport.opener
        pools = {n: PooledOpener('https://www.googleapis.com', original, maximum=n) for n in (2, 4)}
        baseline = None
        for size, label in [(2,'two_cold'), (4,'four_cold'), (4,'four_warm'), (2,'two_warm')]:
            counted = Counted(pools[size]);reader.transport.opener = counted
            active = peak = 0
            guard = threading.Lock()
            def read(native_id):
                nonlocal active, peak
                with guard:
                    active += 1;peak = max(peak, active)
                try:
                    version = baseline[native_id]['version'] if baseline else None
                    return reader.read(actor, native_id, version)
                finally:
                    with guard: active -= 1
            started = time.perf_counter();items = []
            for start in range(0, len(native_ids), size):
                batch = native_ids[start:start+size]
                with ThreadPoolExecutor(max_workers=size) as executor:
                    items.extend(zip(batch, executor.map(read, batch)))
                if any(decision.result != 'allow' for _, (decision, _) in items): break
            elapsed = time.perf_counter()-started
            good = len(items) == len(native_ids) and all(d.result == 'allow' and c is not None for _,(d,c) in items)
            contents = {native_id: content for native_id,(_,content) in items}
            same = good and (baseline is None or contents == baseline)
            result['samples'].append({'configuration':label,'seconds':elapsed,'native_reads':len(items),
                'native_http_requests':counted.count,'peak_full_reads':peak,
                'all_allowed':good,'same_content_as_first':same})
            if not same:
                result['status'] = 'stopped_source_or_content_change';break
            if baseline is None: baseline = contents
        else: result['status'] = 'completed'
    except Exception as error:
        result['status'] = 'stopped';result['error_category'] = type(error).__name__
    finally:
        for pool in pools.values(): pool.close()
        write_private(target, json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result.get('status') == 'completed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
