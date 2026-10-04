import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_live_seed import prepare


class LiveSeed(unittest.TestCase):
    def test_complete_plan_preserves_restricted_child_and_unverified_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'seed'
            manifest = prepare(out)
            self.assertEqual(len(manifest['resources']), 13)
            self.assertEqual(len(manifest['identities']), 6)
            rows = {r['fixture_id']: r for r in manifest['resources']}
            self.assertEqual(rows['J-01-comment-sec']['expected_readers'], ['security'])
            self.assertNotIn('eng_b', rows['S-01']['expected_readers'])
            self.assertIn('eng_b', rows['S-02']['expected_readers'])
            self.assertEqual(rows['J-01-comment-sec']['parent_fixture_id_or_group'], 'J-01')
            for row in rows.values():
                self.assertIsNone(row['native_id'])
                self.assertFalse(row['live_acl_verified'])
                self.assertEqual(row['status'], 'not_seeded')
                self.assertEqual(hashlib.sha256((out / row['content_path']).read_bytes()).hexdigest(), row['content_sha256'])
            before = (out / 'manifest.json').read_bytes()
            with self.assertRaises(FileExistsError):
                prepare(out)
            self.assertEqual(before, (out / 'manifest.json').read_bytes())
            self.assertEqual(json.loads(before), manifest)
