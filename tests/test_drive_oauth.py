import base64
import contextlib
import hashlib
import io
import json
import os
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import Mock,patch
from urllib.parse import parse_qs,urlsplit,urlencode

from brain.drive_oauth import DesktopClient,load_client,Consent,authorize,verify_account,SCOPE,AUTH,TOKEN,ISSUER
from brain.confluence import SourceUnavailable
from scripts.drive_query import load_oauth_reader

CLIENT='fixture.apps.googleusercontent.com'
EMAIL='fixture@example.com'


class OAuthBoundary(unittest.TestCase):
    def setUp(self):self.client=DesktopClient(CLIENT,'fixture-secret');self.flow=Consent(self.client,12345)
    def target(self,**changes):
        return '/oauth/callback?'+urlencode(dict(state=self.flow.state,code='fixture-code',iss=ISSUER,**changes))
    def test_pkce_fixed_endpoints_scope_and_no_secret_in_authorization_url(self):
        q=parse_qs(urlsplit(self.flow.url(EMAIL)).query)
        expected=base64.urlsafe_b64encode(hashlib.sha256(self.flow.verifier.encode()).digest()).decode().rstrip('=')
        self.assertEqual(q['code_challenge'],[expected]);self.assertEqual(q['code_challenge_method'],['S256'])
        self.assertEqual(q['scope'],[SCOPE]);self.assertEqual(q['include_granted_scopes'],['false'])
        self.assertEqual(q['access_type'],['online']);self.assertNotIn('fixture-secret',self.flow.url(EMAIL))
        self.assertNotIn('fixture-secret',repr(self.client))
    def test_callback_rejects_forgery_duplicates_wrong_path_host_origin_and_replay(self):
        host='127.0.0.1:12345'
        for target,h,origin in [(self.target()+'&state=other',host,None),
                (self.target().replace(self.flow.state,'other'),host,None),
                (self.target()+'&role=admin',host,None),(self.target(),'evil.example',None),
                (self.target(),host,'https://evil.example'),('/wrong?state='+self.flow.state,host,None),
                ('/oauth/callback?state=%E9%94%99&code=x',host,None)]:
            self.assertEqual(self.flow.callback(target,h,origin),400)
            self.assertFalse(self.flow.finished)
        self.assertEqual(self.flow.callback(self.target(),host),200)
        self.assertEqual(self.flow.callback(self.target(),host),400)
    def test_expired_and_denied_consent_never_exchanges(self):
        transport=Mock();self.flow.expires=0
        self.assertEqual(self.flow.callback(self.target(),'127.0.0.1:12345'),400)
        with self.assertRaises(SourceUnavailable):self.flow.exchange(transport)
        transport.exchange.assert_not_called()
        denied=Consent(self.client,12345)
        self.assertEqual(denied.callback('/oauth/callback?'+urlencode({'state':denied.state,'error':'access_denied','iss':ISSUER}),
                                        '127.0.0.1:12345'),403)
        with self.assertRaises(SourceUnavailable):denied.exchange(transport)
        transport.exchange.assert_not_called()
    def test_google_issuer_is_required_exact_and_not_duplicated(self):
        host='127.0.0.1:12345'
        for issuer in (None,'https://evil.example','https://accounts.google.com/','accounts.google.com'):
            query={'state':self.flow.state,'code':'fixture-code'}
            if issuer is not None: query['iss']=issuer
            self.assertEqual(self.flow.callback('/oauth/callback?'+urlencode(query),host),400)
            self.assertEqual(self.flow.reason,'callback_issuer_mismatch')
            self.assertFalse(self.flow.finished);self.assertIsNone(self.flow.code)
        self.assertEqual(self.flow.callback(self.target()+'&iss='+ISSUER,host),400)
        self.assertEqual(self.flow.reason,'callback_duplicate_parameter')
        self.assertEqual(self.flow.callback(self.target(),host),200)
    def test_diagnostic_reason_never_reflects_callback_values(self):
        host='127.0.0.1:12345'
        target='/oauth/callback?'+urlencode({'state':'secret-looking-state','code':'secret-looking-code','iss':ISSUER})
        self.assertEqual(self.flow.callback(target,host),400)
        self.assertEqual(self.flow.reason,'callback_state_mismatch')
        self.assertNotIn('secret-looking',self.flow.reason)
    def test_exchange_checks_exact_granted_scope_type_lifetime_and_one_use_code(self):
        valid={'token_type':'Bearer','scope':SCOPE,'expires_in':3600,'access_token':'fixture-token','refresh_token':'ignored-fixture-refresh'}
        for changes in ({'scope':SCOPE+' other'},{'scope':''},{'token_type':'other'},{'expires_in':0},
                        {'expires_in':True},{'access_token':'bad token'},{}):
            flow=Consent(self.client,12345);flow.callback('/oauth/callback?'+urlencode({'state':flow.state,'code':'fixture-code','iss':ISSUER}),'127.0.0.1:12345')
            transport=Mock();transport.exchange.return_value=(200,dict(valid,**changes))
            if changes:
                with self.assertRaises(SourceUnavailable):flow.exchange(transport)
            else:self.assertEqual(flow.exchange(transport),'fixture-token')
            with self.assertRaises(SourceUnavailable):flow.exchange(transport)
            transport.exchange.assert_called_once()
            self.assertEqual(transport.exchange.call_args.args[0]['code_verifier'],flow.verifier)
    def test_native_email_and_permission_id_binding_cannot_be_substituted(self):
        transport=Mock();good={'me':True,'permissionId':'NATIVE123','emailAddress':EMAIL}
        for user in [dict(good,emailAddress='different@example.com'),dict(good,me=False),dict(good,permissionId='bad/id')]:
            transport.get.return_value=(200,{'user':user})
            with self.assertRaises(SourceUnavailable):verify_account('fixture-token',EMAIL,transport)
        transport.get.return_value=(200,{'user':good})
        result=verify_account('fixture-token',EMAIL,transport);self.assertEqual(result.account_id,'NATIVE123')
        self.assertIn('emailAddress',transport.get.call_args.args[0]);self.assertNotIn('/files',transport.get.call_args.args[0])
    def test_client_permissions_and_endpoint_substitution_rejected_without_secret_output(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'client.json'
            good={'client_id':CLIENT,'client_secret':'fixture-secret','auth_uri':AUTH,'token_uri':TOKEN}
            p.write_text(json.dumps({'installed':good}));p.chmod(0o600)
            self.assertEqual(load_client(p,CLIENT),self.client)
            for changes in ({'token_uri':'https://evil.example/token'},{'client_id':'other.apps.googleusercontent.com'}):
                p.write_text(json.dumps({'installed':dict(good,**changes)}))
                with self.assertRaises(ValueError):load_client(p,CLIENT)
            p.write_text(json.dumps({'installed':good}));p.chmod(0o644)
            with self.assertRaises(ValueError):load_client(p,CLIENT)
            link=Path(folder)/'link';link.symlink_to(p)
            with self.assertRaises(OSError):load_client(link,CLIENT)


class OAuthLoopback(unittest.TestCase):
    def test_actual_http_callback_has_no_secret_reflection_and_exchanges_once(self):
        transport=Mock();transport.exchange.return_value=(200,{'token_type':'Bearer','scope':SCOPE,'expires_in':3600,'access_token':'fixture-token'})
        results=[];threads=[]
        def notify(url):
            q=parse_qs(urlsplit(url).query)
            def request():
                with urllib.request.urlopen(q['redirect_uri'][0]+'?'+urlencode({'state':q['state'][0],'code':'fixture-code','iss':ISSUER}),timeout=5) as response:
                    results.append((response.status,response.read().decode(),dict(response.headers)))
            thread=threading.Thread(target=request);threads.append(thread);thread.start()
        result=authorize(DesktopClient(CLIENT,'fixture-secret'),EMAIL,notify,transport=transport)
        for thread in threads:thread.join()
        self.assertEqual(result,'fixture-token');self.assertEqual(results[0][0],200)
        self.assertNotIn('fixture-code',results[0][1]);self.assertNotIn('fixture-token',results[0][1])
        self.assertEqual(results[0][2]['Cache-Control'],'no-store');transport.exchange.assert_called_once()


class OAuthOperatorConfiguration(unittest.TestCase):
    def config(self,p):
        p.write_text(json.dumps({'approved_synthetic_only':True,'tenant':'pilot','files':{'FILE1':'FOLDER1'},
            'oauth_operator':{'actor':'eng_a','email':EMAIL},'oauth_client_id':CLIENT}))
    def test_invalid_config_stops_before_credentials_or_consent(self):
        with tempfile.TemporaryDirectory() as folder,patch('brain.drive_oauth.load_client') as load,patch('brain.drive_oauth.authorize') as auth:
            p=Path(folder)/'config';self.config(p);data=json.loads(p.read_text());data['files']={'bad/id':'FOLDER1'};p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_oauth_reader(p,'missing','eng_a')
            load.assert_not_called();auth.assert_not_called()
    def test_operator_binds_only_verified_google_account_without_manual_token_prompt(self):
        with tempfile.TemporaryDirectory() as folder,patch('brain.drive_oauth.load_client',return_value=DesktopClient(CLIENT,'fixture-secret')), \
             patch('brain.drive_oauth.authorize',return_value='fixture-token') as auth, \
             patch('brain.drive.DriveTransport') as transport,patch('scripts.drive_query.hidden_token') as prompt:
            transport.return_value.get.return_value=(200,{'user':{'me':True,'permissionId':'NATIVE123','emailAddress':EMAIL}})
            p=Path(folder)/'config';self.config(p);reader=load_oauth_reader(p,'missing','eng_a')
            self.assertEqual(reader.delegations['eng_a'].account_id,'NATIVE123');auth.assert_called_once();prompt.assert_not_called()
            self.assertEqual(transport.return_value.get.call_count,1)
    def test_oauth_cli_requires_live_and_drive_before_loading_any_client(self):
        from brain.operator_web import main
        with patch('scripts.drive_query.load_oauth_reader') as load,contextlib.redirect_stdout(io.StringIO()):
            for args in [[],['--source','jira','--live'],['--source','multi','--live']]:
                self.assertEqual(main(['--config','missing','--oauth-client','missing',*args]),2)
            load.assert_not_called()
    def test_reserved_port_conflict_prevents_google_consent_or_credential_read(self):
        import errno
        from brain.operator_web import main
        with patch('brain.operator_web.create_server',side_effect=OSError(errno.EADDRINUSE,'private')), \
             patch('scripts.drive_query.load_oauth_reader') as load,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--source','drive','--live','--config','missing','--oauth-client','missing']),2)
            load.assert_not_called()
