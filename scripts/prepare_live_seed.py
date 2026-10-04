"""Prepare synthetic onboarding artifacts locally; never calls a platform API."""
import argparse
import hashlib
import json
from pathlib import Path

from brain.sources import BASELINE, FixtureWorld
from brain.contracts import Actor, TENANT


def prepare(output):
    output = Path(output)
    # Exclusive creation prevents silently overwriting a reviewed seed package.
    output.mkdir(parents=True, exist_ok=False)
    world = FixtureWorld()
    resources = list(world.resources.values())
    manifest = {
        'schema_version': 1, 'synthetic': True, 'mode': 'local_seed_plan_only',
        'baseline_sha256': hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        'identities': {uid: {'platform_account': None, 'fixture': user}
                       for uid, user in world.users.items()},
        'resources': [],
    }
    for resource in resources:
        relative = Path(resource['source']) / (resource['id'] + '.md')
        target = output / relative
        target.parent.mkdir(exist_ok=True)
        target.write_text(
            '# ' + resource['title'] + '\n\n'
            '> SYNTHETIC COMPETITION TEST DATA — not an actual company record.\n\n'
            + resource['text'] + '\n', encoding='utf-8')
        allowed = []
        for uid in world.users:
            if world.adapter(resource['source']).check_read(
                    Actor(uid, TENANT), resource['id']).result == 'allow':
                allowed.append(uid)
        manifest['resources'].append({
            'fixture_id': resource['id'], 'source': resource['source'],
            'content_path': relative.as_posix(),
            'content_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'parent_fixture_id_or_group': resource['parent'],
            'links': resource.get('links', []),
            'fixture_policy': resource['policy'],
            'expected_readers': allowed,
            'native_id': None, 'native_url': None,
            'live_acl_verified': False, 'status': 'not_seeded',
        })
    (output / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, help='new local directory')
    args = parser.parse_args()
    result = prepare(args.out)
    print('Prepared %d synthetic objects; no platform calls performed.' % len(result['resources']))
