import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from brain.confluence import JsonTransport,SourceRateLimited
from brain.contracts import Actor
from brain.delegated_query import DelegatedQueryPilot
from brain.discovery import ContainerDiscovery
from brain.drive import DriveTransport
from brain.source_cooldown import SourceCooldownTransport
from test_container_discovery import setup


class SourceCooldownTests(unittest.TestCase):
    def test_constructor_wraps_once_and_all_discovery_readers_share_deadline(self):
        store,_,http,readers=setup();self.addCleanup(store.db.close)
        class Native(JsonTransport):
            def get(self,*args):return http['confluence'].get(*args)
        readers['confluence'].transport=Native()
        pilot=DelegatedQueryPilot(readers,store,live=True)
        shared=pilot.authority.readers['confluence'].transport
        self.assertIsInstance(shared,SourceCooldownTransport)
        worker=ContainerDiscovery(pilot,Actor('eng_b','pilot'))
        self.assertIs(worker.base_readers['confluence'].transport,shared)
        self.assertIs(worker._reader('confluence',{'98564':None}).transport,shared)
        second=DelegatedQueryPilot(readers,store,live=True)
        self.assertIs(second.authority.readers['confluence'].transport,shared)

    def test_already_admitted_read_finishes_but_new_read_is_rejected_after_429(self):
        import threading
        entered=threading.Event();release=threading.Event();calls=[];results=[]
        class Delegate:
            def get(self,label):
                calls.append(label)
                if label=='rate':raise SourceRateLimited(600)
                entered.set()
                if not release.wait(2):raise RuntimeError('Test release missing')
                return 200,{'ok':True}
        transport=SourceCooldownTransport(Delegate())
        thread=threading.Thread(target=lambda:results.append(transport.get('admitted')),daemon=True)
        thread.start()
        try:
            self.assertTrue(entered.wait(1))
            with self.assertRaises(SourceRateLimited):transport.get('rate')
            with self.assertRaises(SourceRateLimited):transport.get('new')
            self.assertEqual(calls,['admitted','rate'])
        finally:release.set();thread.join(2)
        self.assertEqual(results,[(200,{'ok':True})])

    def test_shared_deadline_blocks_body_and_metadata_without_retry_then_recovers(self):
        calls=[];clock=[0]
        class Delegate:
            def get(self,*args):calls.append('get');raise SourceRateLimited(600)
            def media(self,*args):calls.append('media');return 200,b'body'
        transport=SourceCooldownTransport(Delegate(),clock=lambda:clock[0])
        with self.assertRaises(SourceRateLimited):transport.get('unused')
        clock[0]=120
        with self.assertRaises(SourceRateLimited) as caught:transport.media('unused')
        self.assertEqual(caught.exception.retry_after,480);self.assertEqual(calls,['get'])
        clock[0]=600;self.assertEqual(transport.media('unused'),(200,b'body'))
        self.assertEqual(calls,['get','media'])

    def test_reader_unknown_keeps_cooldown_for_discovery_and_foreground(self):
        store,pilot,http,readers=setup();self.addCleanup(store.db.close)
        actor=Actor('eng_b','pilot');worker=ContainerDiscovery(pilot,actor)
        worker.run_once();resource=store.get('confluence:98565');clock=[0];attempts=[]
        class Limited(JsonTransport):
            def get(self,*args):attempts.append(1);raise SourceRateLimited(600)
        cooldown=SourceCooldownTransport(Limited(),clock=lambda:clock[0])
        pilot.authority.readers['confluence'].transport=cooldown
        worker.base_readers['confluence'].transport=cooldown
        decision=pilot.authority.check_read(actor,resource['id'])
        self.assertEqual(decision.result,'unknown')
        clock[0]=120
        with self.assertRaises(SourceRateLimited) as caught:worker._credential('confluence',worker.base_readers['confluence'])
        self.assertEqual(caught.exception.retry_after,480)
        self.assertEqual(pilot.authority.check_read(actor,resource['id']).result,'unknown')
        self.assertEqual(len(attempts),1)

    def test_real_media_transport_preserves_numeric_retry_after(self):
        transport=DriveTransport()
        error=HTTPError('https://unused',429,'rate limited',{'Retry-After':'600'},None)
        with patch.object(transport.opener,'open',side_effect=error):
            with self.assertRaises(SourceRateLimited) as caught:transport.media('FILE1','Bearer fake')
        self.assertEqual(caught.exception.retry_after,600)
