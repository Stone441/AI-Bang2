"""Local Mac signal renewal safeguards; no browser or external source calls."""
import io,json,os,signal,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from scripts.local_entry import renew


class LocalEntry(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.control=self.root/'.runtime/delivery-trial-20261011/entry-server.json'
        self.token=self.root/'.runtime/page-failure-ux-logs/human-bootstrap-token'
        for p in (self.control.parent,self.token.parent):p.mkdir(parents=True,mode=0o700)
        self.version={'startup_source_sha256':'fixture','process_loaded_at':'fixture'}
        self.control.write_text(json.dumps({'pid':1234,'port':49161,'runtime_version':self.version}));self.control.chmod(0o600)
        self.token.write_text('old');self.token.chmod(0o600)
        self.health={'auth_kind':'operator','runtime_version':self.version}

    def response(self):return io.BytesIO(json.dumps(self.health).encode())

    def test_renew_signals_verified_own_listener_and_keeps_token_private(self):
        def signal_handler(pid,sig):
            self.assertEqual((pid,sig),(1234,signal.SIGUSR1))
            self.token.write_text('N'*44);self.token.chmod(0o600)
        with patch('scripts.local_entry.urlopen',side_effect=lambda *a,**k:self.response()), \
             patch('scripts.local_entry.subprocess.run',return_value=Mock(stdout='p1234\nn127.0.0.1:49161\n')), \
             patch('scripts.local_entry.os.kill',side_effect=signal_handler) as kill:
            self.assertEqual(renew(self.root),'N'*44);kill.assert_called_once()

    def test_check_is_read_only_even_with_old_token(self):
        with patch('scripts.local_entry.urlopen',side_effect=lambda *a,**k:self.response()), \
             patch('scripts.local_entry.subprocess.run',return_value=Mock(stdout='p1234\nn127.0.0.1:49161\n')), \
             patch('scripts.local_entry.os.kill') as kill:
            self.assertIsNone(renew(self.root,check_only=True));kill.assert_not_called()
            self.assertEqual(self.token.read_text(),'old')

    def test_reviewer_password_entry_does_not_issue_operator_ticket(self):
        self.health['auth_kind']='reviewer'
        with patch('scripts.local_entry.urlopen',side_effect=lambda *a,**k:self.response()), \
             patch('scripts.local_entry.subprocess.run',return_value=Mock(stdout='p1234\nn127.0.0.1:49161\n')), \
             patch('scripts.local_entry.os.kill') as kill:
            self.assertIsNone(renew(self.root));kill.assert_not_called()

    def test_wrong_startup_or_listener_never_receives_signal(self):
        for wrong in ('startup','listener'):
            with self.subTest(wrong=wrong):
                self.health['runtime_version']={'different':True} if wrong=='startup' else self.version
                with patch('scripts.local_entry.urlopen',side_effect=lambda *a,**k:self.response()), \
                     patch('scripts.local_entry.subprocess.run',return_value=Mock(stdout='p9999\nn127.0.0.1:49161\n')), \
                     patch('scripts.local_entry.os.kill') as kill:
                    with self.assertRaises(ValueError):renew(self.root)
                    kill.assert_not_called()

    def test_symlink_or_loose_permissions_stop_before_signal(self):
        original=self.control.read_text();self.control.unlink()
        target=self.root/'target';target.write_text(original);self.control.symlink_to(target)
        with patch('scripts.local_entry.os.kill') as kill:
            with self.assertRaises(ValueError):renew(self.root)
            kill.assert_not_called()
        self.control.unlink();self.control.write_text(original);self.control.chmod(0o644)
        with patch('scripts.local_entry.os.kill') as kill:
            with self.assertRaises(ValueError):renew(self.root)
            kill.assert_not_called()
        self.control.chmod(0o600);self.token.unlink();self.token.symlink_to(target)
        with patch('scripts.local_entry.os.kill') as kill:
            with self.assertRaises(ValueError):renew(self.root)
            kill.assert_not_called()

    def test_public_entry_checks_owned_local_process_with_exact_host(self):
        from scripts.local_entry import entry_url
        body=json.loads(self.control.read_text());body['public_origin']='https://contextledger.hellokyleshi.com'
        self.control.write_text(json.dumps(body));self.health['auth_kind']='reviewer'
        with patch('scripts.local_entry.urlopen',side_effect=lambda *a,**k:self.response()) as read, \
             patch('scripts.local_entry.subprocess.run',return_value=Mock(stdout='p1234\nn127.0.0.1:49161\n')):
            renew(self.root,check_only=True)
            request=read.call_args.args[0]
            self.assertEqual(request.full_url,'http://127.0.0.1:49161/api/health')
            self.assertEqual(request.get_header('Host'),'contextledger.hellokyleshi.com')
        self.assertEqual(entry_url(self.root),'https://contextledger.hellokyleshi.com/')
        body['public_origin']='https://unapproved.example';self.control.write_text(json.dumps(body))
        with self.assertRaises(ValueError):entry_url(self.root)
