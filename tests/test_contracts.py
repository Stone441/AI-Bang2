import unittest
from brain.sources import FixtureWorld
from brain.contracts import Actor, SOURCES

class Contracts(unittest.TestCase):
    def test_complete_matrix(self):
        world=FixtureWorld()
        expected={
            'C-01':{'eng_a','eng_b','security'},'C-02':{'eng_a','eng_b','product_ops','contractor','security'},
            'C-03':{'security'},'J-01':{'eng_a','eng_b','security'},'J-01-comment-sec':{'security'},
            'J-02':{'eng_a','eng_b','product_ops','security'},'J-03':{'eng_a','eng_b','product_ops','security'},
            'S-01':{'eng_a','security'},'S-02':{'eng_a','eng_b','product_ops','security'},'S-03':{'eng_a','contractor'},
            'D-01':{'eng_a','eng_b','security'},'D-02':{'eng_a','eng_b','product_ops','security'},'D-03':{'eng_a','eng_b','product_ops','security'}}
        self.assertEqual(set(expected),set(world.resources))
        for rid,allowed in expected.items():
            for uid in world.users:
                with self.subTest(resource=rid,user=uid):
                    actual=world.adapter(world.resources[rid]['source']).check_read(Actor(uid),rid)
                    self.assertEqual(actual.result,'allow' if uid in allowed else 'deny')

    def test_pagination_and_identity_boundary(self):
        w=FixtureWorld()
        for source in SOURCES:
            adapter=w.adapter(source)
            cursor=0; items=[]
            while cursor is not None:
                page=adapter.list_initial(cursor,1); items+=page['items']; cursor=page['next_cursor']
            self.assertEqual(len(items),len([r for r in w.resources.values() if r['source']==source]))
            rid=items[0]['id']
            self.assertEqual(adapter.check_read(Actor('eng_a','other-tenant'),rid).result,'deny')
            self.assertEqual(adapter.check_read(Actor('unknown'),rid).result,'unknown')
            w.faults.add(source)
            self.assertEqual(adapter.check_read(Actor('eng_a'),rid).result,'unknown')

    def test_fixture_schema_and_locators(self):
        w=FixtureWorld()
        self.assertEqual(len(w.resources),13)
        self.assertEqual(len(w.users),6)
        for r in w.resources.values():
            self.assertTrue(r['locator'])
            self.assertTrue(r['source_url'].startswith('fixture://'))
            self.assertEqual(r['tenant'],'synthetic-demo')
