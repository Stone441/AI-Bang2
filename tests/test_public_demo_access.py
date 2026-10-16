import json
from pathlib import Path
import tempfile
import time
import unittest
from scripts.public_demo_access import load_public_accounts
from brain.reviewer_access import ReviewAccounts

class PublicDemoAccessTests(unittest.TestCase):
    def test_only_exact_authorized_set_with_matching_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);registry=root/'registry.json';public=root/'public.json'
            salt='a'*32
            def account():return dict(active=True,expires=time.time()+3600,revision='b'*16,salt=salt,password_hash=ReviewAccounts.derive('fixture-only',salt))
            accounts={name:account() for name in ['engineer','product','partner']}
            auditor=account();auditor.update(resource_scope='payment-service',viewer_ids=['reviewer:'+k+':'+v['revision'] for k,v in accounts.items()])
            body={'accounts':accounts,'application_auditors':{'auditor':auditor}}
            rows=[dict(username=k,password='fixture-only',label=k) for k in [*accounts,'auditor']]
            registry.write_text(json.dumps(body));public.write_text(json.dumps(rows))
            self.assertEqual(len(load_public_accounts(public,registry)),4)
            rows[-1]['password']='wrong';public.write_text(json.dumps(rows))
            with self.assertRaises(ValueError):load_public_accounts(public,registry)
            rows[-1]['password']='fixture-only';public.write_text(json.dumps(rows))
            auditor['viewer_ids'].append('reviewer:unrelated:'+'c'*16);registry.write_text(json.dumps(body))
            with self.assertRaises(ValueError):load_public_accounts(public,registry)
            auditor['viewer_ids'].pop();auditor['expires']=0;registry.write_text(json.dumps(body))
            with self.assertRaises(ValueError):load_public_accounts(public,registry)
