"""Validate explicitly published demo credentials; including the explicitly authorized scoped auditor."""
import json
import time
import hmac
from pathlib import Path
from brain.reviewer_access import ReviewAccounts


def load_public_accounts(path, registry):
    rows=json.loads(Path(path).read_text())
    body=json.loads(Path(registry).read_text());accounts=body['accounts']
    auditors=body.get('application_auditors',{})
    expected_viewers={'reviewer:'+k+':'+a['revision'] for k,a in accounts.items()}
    if len(accounts)!=3 or len(auditors)!=1:
        raise ValueError('Three demo accounts and one scoped auditor required')
    for a in auditors.values():
        if a.get('resource_scope')!='payment-service' or set(a.get('viewer_ids',[]))!=expected_viewers:
            raise ValueError('Auditor must be limited to these three demo accounts')
    accounts={**accounts,**auditors}
    if not isinstance(rows,list) or len(rows)!=4:
        raise ValueError('Exactly four authorized demo accounts required')
    names=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'username','password','label'}:
            raise ValueError('Invalid public account fields')
        if any(not isinstance(v,str) or not v or len(v)>256 for v in row.values()):
            raise ValueError('Invalid public account values')
        account=next((a for k,a in accounts.items() if a.get('login_name',k)==row['username']),None)
        if row['username'] in names or not account or not account['active'] or account['expires']<=time.time():
            raise ValueError('Active authorized demo account required')
        if not hmac.compare_digest(ReviewAccounts.derive(row['password'],account['salt']),account['password_hash']):
            raise ValueError('Public credentials must match the existing account')
        names.add(row['username'])
    return rows
