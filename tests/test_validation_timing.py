import json
import threading
import unittest
from brain.confluence import JsonTransport
from scripts.validation_timing import Measurements, TimedNativeTransport


class TimingTests(unittest.TestCase):
    def test_delegation_privacy_and_error(self):
        class Delegate:
            def get(self, path, headers=None):
                return (path, headers)
            def media(self, path):
                raise RuntimeError('delegate failure')
        measured = Measurements()
        transport = TimedNativeTransport(Delegate(), measured, 'drive')
        self.assertIsInstance(transport, JsonTransport)
        with measured.phase('query'):
            self.assertEqual(transport.get('secret-url', headers={'Authorization': 'secret-token'}),
                             ('secret-url', {'Authorization': 'secret-token'}))
            with self.assertRaisesRegex(RuntimeError, 'delegate failure'):
                transport.media('secret-url')
        samples = measured.summary('query')['samples']
        self.assertEqual(len(samples), 2)
        self.assertNotIn('secret', json.dumps(samples))
        self.assertTrue(all(s['seconds'] >= 0 for s in samples))

    def test_background_and_nested_phases_are_separate(self):
        measured = Measurements()
        with measured.phase('query'):
            worker = threading.Thread(target=lambda: measured.call('native_http', 'slack', lambda: None))
            worker.start()
            worker.join()
            with measured.phase('preview'):
                measured.call('authorization', 'slack', lambda: None)
            measured.call('generation', 'deepseek', lambda: None)
        self.assertEqual(len(measured.summary('background_discovery')['samples']), 1)
        self.assertEqual(len(measured.summary('preview')['samples']), 1)
        self.assertEqual([s['category'] for s in measured.summary('query')['samples']], ['generation'])

    def test_lock_wait_releases_original_lock_on_failure(self):
        measured = Measurements()
        lock = threading.RLock()
        with measured.phase('query'):
            with self.assertRaises(RuntimeError):
                with measured.acquire(lock):
                    raise RuntimeError('failure')
        acquired = []
        def other_thread():
            acquired.append(lock.acquire(blocking=False))
            if acquired[-1]: lock.release()
        worker = threading.Thread(target=other_thread)
        worker.start()
        worker.join()
        self.assertEqual(acquired, [True])
        self.assertEqual([s['category'] for s in measured.summary('query')['samples']], ['lock_wait'])
