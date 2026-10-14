import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from brain.drive_oauth import RenewableDriveCredential
from brain.confluence import Delegation,SourceUnavailable
class Renewal(unittest.TestCase):
 def test_expiry_and_parallel_refresh(self):
  now=[10];p=RenewableDriveCredential(None,'refresh','test@example.com',None,'id',clock=lambda:now[0])
  with patch('brain.drive_oauth.refresh_access',return_value=('token',100)) as refresh,patch('brain.drive_oauth.verify_account',return_value=Delegation('id','Bearer token')):
   with ThreadPoolExecutor(4) as pool:results=list(pool.map(lambda _:p(),range(8)))
   self.assertEqual(refresh.call_count,1);self.assertEqual(len(results),8)
   now[0]=99;p();self.assertEqual(refresh.call_count,1)
   now[0]=100;p();self.assertEqual(refresh.call_count,2)
 def test_refresh_failure_never_reuses_expired_or_wrong_account(self):
  now=[0];p=RenewableDriveCredential(None,'refresh','test@example.com',None,'id',clock=lambda:now[0])
  with patch('brain.drive_oauth.refresh_access',return_value=('token',100)),patch('brain.drive_oauth.verify_account',return_value=Delegation('id','Bearer token')):p()
  now[0]=100
  with patch('brain.drive_oauth.refresh_access',side_effect=SourceUnavailable):
   with self.assertRaises(SourceUnavailable):p()
  self.assertIsNone(p.current)
  with patch('brain.drive_oauth.refresh_access',return_value=('token',100)),patch('brain.drive_oauth.verify_account',return_value=Delegation('other','Bearer token')):
   with self.assertRaises(SourceUnavailable):p()
  self.assertIsNone(p.current)
