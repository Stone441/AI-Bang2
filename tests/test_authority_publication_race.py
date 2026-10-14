"""Offline prerequisite for future request isolation; production locks remain.

The direct check_many call deliberately omits the outer query lock to expose
late-response races deterministically. This does not test parallel HTTP support.
"""
import copy
import threading
import unittest
from unittest.mock import patch
import test_paired_authorization as paired


class PublicationRace(unittest.TestCase):
    prepare=paired.PairedAuthorization.prepare

    def race(self, mutate):
        store,pilot,_,actor=self.prepare(count=2)
        authority=pilot.authority
        self.assertIs(authority.state_lock,pilot.lock)
        resource=next(r for r in store.resources() if r['source']=='confluence')
        before=copy.deepcopy(authority.resources[resource['id']])
        original=authority._checked_read
        ready,release=threading.Event(),threading.Event()
        result=[];failures=[]

        def delayed(*args):
            response=original(*args)
            ready.set()
            if not release.wait(3):raise RuntimeError('Test synchronization failed')
            return response

        def query():
            try:result.extend(authority.check_many(actor,[resource],phase='review_dispatch'))
            except Exception as error:failures.append(error)

        with patch.object(authority,'_checked_read',side_effect=delayed):
            thread=threading.Thread(target=query,daemon=True);thread.start()
            try:
                self.assertTrue(ready.wait(3))
                with pilot.lock:
                    mutate(authority.resources,resource['id'])
                    published=copy.deepcopy(authority.resources.get(resource['id']))
            finally:
                release.set();thread.join(3)
        self.assertFalse(thread.is_alive());self.assertEqual(failures,[])
        return result[0],before,published,authority.resources.get(resource['id'])

    def test_new_version_deletion_missing_content_and_tenant_change_reject_late_allow(self):
        def version(resources,rid):resources[rid]=dict(resources[rid],version=resources[rid]['version']+1)
        def deleted(resources,rid):resources[rid]=dict(resources[rid],active=False)
        def missing(resources,rid):resources.pop(rid)
        def content(resources,rid):resources[rid]['text']+=' New counterevidence.'
        def tenant(resources,rid):resources[rid]['tenant']='another-tenant'
        def locator(resources,rid):resources[rid]['locator']['changed']='new section'
        for mutate in (version,deleted,missing,content,tenant,locator):
            with self.subTest(change=mutate.__name__):
                decision,before,published,after=self.race(mutate)
                self.assertEqual(decision.result,'unknown')
                self.assertEqual(decision.method,'concurrent-authority-change')
                self.assertEqual(after,published)
                self.assertNotEqual(after,before)

    def test_equal_source_refresh_keeps_newer_observation_metadata(self):
        def observation(resources,rid):
            resources[rid]=dict(resources[rid],observed_at='2030-01-01T00:00:00Z',
                                source_confirmed_at='2026-10-13T00:00:00Z')
        decision,_,published,after=self.race(observation)
        self.assertEqual(decision.result,'allow')
        self.assertEqual(after['observed_at'],published['observed_at'])
        self.assertEqual(after['source_confirmed_at'],published['source_confirmed_at'])
