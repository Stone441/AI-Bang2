"""Fake authoritative sources, independent of indexed ACL snapshots."""
import copy
import json
from pathlib import Path
from .contracts import Actor, Decision, SOURCES, TENANT, now

BASELINE = Path(__file__).resolve().parents[1] / 'fixtures/baseline.json'


def policy_allows(user_id, user, policy):
    groups = set(user['groups'])
    kind = policy['kind']
    if kind == 'confluence':
        return bool(groups.intersection(policy['space_groups'])) and bool(groups.intersection(policy['page_groups']))
    if kind == 'jira':
        return (bool(groups.intersection(policy['project_groups']))
                and bool(groups.intersection(policy['issue_groups']))
                and (policy.get('comment_groups') is None or bool(groups.intersection(policy['comment_groups']))))
    if kind == 'slack':
        return user_id in policy['members'] if policy['private'] else 'staff' in groups
    if kind == 'drive':
        return user_id in policy['direct_users'] or bool(groups.intersection(policy['inherited_groups']))
    return False


class FixtureWorld:
    def __init__(self, path=BASELINE):
        self.baseline = json.loads(Path(path).read_text())
        if self.baseline.get('synthetic') is not True:
            raise ValueError('Only synthetic fixtures are authorized')
        self.users = copy.deepcopy(self.baseline['users'])
        self.resources = {r['id']: copy.deepcopy(r) for r in self.baseline['resources']}
        self.events = []
        self.faults = set()
        self.revoked = set()

    def adapter(self, source):
        if source not in SOURCES:
            raise ValueError('Unknown source')
        return FixtureAdapter(self, source)

    def mutate(self, rid, kind, **changes):
        """Test management only; never reachable from the employee API."""
        r = self.resources[rid]
        if kind == 'revoke':
            self.revoked.add((changes['user_id'], rid))
            r['policy_version'] += 1
        elif kind == 'delete':
            r['active'] = False
        elif kind == 'content':
            r.update(changes)
            r['version'] = changes.get('version', r['version'])
        else:
            raise ValueError('Unsupported fixture mutation')
        event = {'event_id': len(self.events)+1, 'resource_id':rid, 'kind':kind,
                 'observed_at':now(), 'snapshot':copy.deepcopy(r)}
        self.events.append(event)
        return event


class FixtureAdapter:
    def __init__(self, world, source):
        self.world, self.source = world, source

    def capabilities(self):
        return {'source':self.source, 'status':'fixture_only', 'live':'blocked',
                'authority':'independent in-process synthetic policy', 'dm':False}

    def list_initial(self, cursor=0, limit=100):
        values = [copy.deepcopy(r) for r in self.world.resources.values() if r['source']==self.source]
        items = values[cursor:cursor+limit]
        return {'items':items,'next_cursor':cursor+len(items) if cursor+len(items)<len(values) else None}

    def list_changes(self, cursor=0, limit=100):
        events=[copy.deepcopy(e) for e in self.world.events if e['event_id']>cursor and e['snapshot']['source']==self.source]
        items=events[:limit]
        return {'items':items,'next_cursor':items[-1]['event_id'] if items else cursor}

    def fetch_resource(self, rid):
        r = self.world.resources[rid]
        if r['source'] != self.source:
            raise KeyError(rid)
        return copy.deepcopy(r)

    def check_read(self, actor: Actor, rid):
        r = self.world.resources.get(rid)
        result = 'deny'
        if self.source in self.world.faults or actor.user_id not in self.world.users:
            result = 'unknown'
        elif r and r['source']==self.source and r['tenant']==actor.tenant==TENANT:
            if r['active'] and (actor.user_id,rid) not in self.world.revoked:
                if policy_allows(actor.user_id, self.world.users[actor.user_id], r['policy']):
                    result = 'allow'
        return Decision(result, now(), 'fixture-current-source-policy', r['policy_version'] if r else 0)

    def source_link(self, rid):
        return self.fetch_resource(rid)['source_url']
