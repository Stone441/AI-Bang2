"""Explicit Mac user entry renewal; fixed local operator only, no HTTP control API."""
import json,os,re,signal,stat,subprocess,time
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlparse


def private_path(path,mode):
    if path.is_symlink() or not path.exists():raise ValueError('本机入口控制尚未准备好。')
    info=path.stat()
    if info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=mode:
        raise ValueError('本机入口文件权限不符合要求。')


def entry_url(root):
    control=root/'.runtime/delivery-trial-20261011/entry-server.json'
    private_path(control.parent,0o700);private_path(control,0o600)
    origin=json.loads(control.read_text()).get('public_origin')
    if origin is None:return 'http://127.0.0.1:49161/'
    # This project's fixed approved host; never open an arbitrary control-file URL.
    if origin!='https://contextledger.hellokyleshi.com':
        raise ValueError('未认可的部署域名。')
    return origin+'/'


def renew(root,*,check_only=False):
    control=root/'.runtime/delivery-trial-20261011/entry-server.json'
    token=root/'.runtime/page-failure-ux-logs/human-bootstrap-token'
    private_path(control.parent,0o700);private_path(control,0o600)
    private_path(token.parent,0o700)
    if token.exists() or token.is_symlink():private_path(token,0o600)
    owner=json.loads(control.read_text())
    pid=owner.get('pid')
    version=owner.get('runtime_version')
    if (type(pid) is not int or pid<=1 or owner.get('port')!=49161
            or not isinstance(version,dict) or not version.get('startup_source_sha256')
            or not version.get('process_loaded_at')):
        raise ValueError('本机入口实例信息不符合要求。')
    endpoint=entry_url(root)
    request=Request('http://127.0.0.1:49161/api/health',headers={'Host':urlparse(endpoint).netloc})
    with urlopen(request,timeout=5) as response:health=json.load(response)
    if health.get('auth_kind') not in ('operator','reviewer') or health.get('runtime_version')!=owner.get('runtime_version'):
        raise ValueError('当前服务与本任务入口实例不一致。')
    listener=subprocess.run(['/usr/sbin/lsof','-a','-p',str(pid),'-iTCP:49161','-sTCP:LISTEN','-n','-P','-Fpn'],
        check=True,capture_output=True,text=True,timeout=5).stdout.splitlines()
    if 'p'+str(pid) not in listener or 'n127.0.0.1:49161' not in listener:
        raise ValueError('当前端口不属于预期的本任务实例。')
    if check_only or health.get('auth_kind')=='reviewer':return None
    before=token.read_bytes() if token.is_file() and not token.is_symlink() else None
    os.kill(pid,signal.SIGUSR1)
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        if token.is_file() and not token.is_symlink():
            private_path(token,0o600)
            value=token.read_bytes()
            if value!=before:
                ticket=value.decode().strip()
                if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}',ticket):raise ValueError('登录码格式异常。')
                return ticket
        time.sleep(.05)
    raise ValueError('本机入口刷新暂未完成；请稍后再双击。')
