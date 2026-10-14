"""Generate private demo account credentials locally; never prints passwords."""
import argparse
import json
import os
from pathlib import Path
import secrets
import time

from brain.reviewer_access import ReviewAccounts


def create(path, cards, tenant, mapping, *, days=7, application_roles=None, demo_roles=None, personas=None):
    path, cards = Path(path), Path(cards)
    if path.exists() or cards.exists() or path.is_symlink() or cards.is_symlink():
        raise ValueError('Use new output paths; existing accounts are never reset')
    accounts, lines = {}, []
    for username, role in mapping.items():
        password = secrets.token_urlsafe(24)
        salt = secrets.token_hex(16)
        accounts[username] = {'source_actor': role, 'active': True,
            'expires': time.time()+days*86400, 'revision': secrets.token_hex(8),
            'salt': salt, 'password_hash': ReviewAccounts.derive(password, salt)}
        if personas and username in personas:
            accounts[username].update(login_name=personas[username][0], display_name=personas[username][1])
        login_name = accounts[username].get('login_name', username)
        lines.extend([f'Username: {login_name}', f'Password: {password}', f'Demo role: {role}', ''])
    if application_roles is not None:
        if set(demo_roles or {}) != set(accounts):raise ValueError('A demo role is required for each account')
        for username,row in accounts.items():row['demo_role']=demo_roles[username]
    body = {'schema': 1, 'purpose': 'shared-synthetic-review',
            'source_tenant': tenant, 'accounts': accounts}
    if application_roles is not None:body['application_roles']=application_roles
    for target, value in ((path, json.dumps(body, indent=2)+'\n'),
                          (cards, 'PRIVATE — demo credentials. Do not commit or upload.\n\n'+'\n'.join(lines))):
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(value)
    return body


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--cards', type=Path, required=True)
    p.add_argument('--tenant', required=True)
    p.add_argument('--account', action='append', required=True, help='username:approved_source_actor')
    p.add_argument('--application-policy', type=Path, help='Trusted JSON: roles and account_roles; exact resource IDs only')
    args = p.parse_args()
    import re
    mapping = {}
    for value in args.account:
        parts = value.split(':')
        if len(parts)!=2 or not all(re.fullmatch(r'[a-z0-9_-]{1,48}', x) for x in parts) or parts[0] in mapping:
            p.error('Unique username:source_actor pairs required')
        mapping[parts[0]] = parts[1]
    policy=json.loads(args.application_policy.read_text()) if args.application_policy else None
    create(args.output, args.cards, args.tenant, mapping,
           application_roles=policy['roles'] if policy else None,
           demo_roles=policy['account_roles'] if policy else None)
    print('Private account registry and login cards created. No model/platform calls.')


if __name__ == '__main__':
    main()
