"""Open only the verified local candidate, never fall back silently to an old service."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.request import urlopen
from urllib.parse import urlparse


def checked_url(path):
    path=Path(path)
    if path.is_symlink() or path.stat().st_uid!=os.getuid() or path.stat().st_mode & 0o077:
        raise ValueError('候选入口文件权限不符合要求。')
    control=json.loads(path.read_text());url=control['url'];parsed=urlparse(url)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or not parsed.port or parsed.path!='/' or parsed.query or parsed.fragment or parsed.username:
        raise ValueError('候选入口不是已核验的本机地址。')
    health=json.load(urlopen(url+'api/health',timeout=5))
    if health.get('auth_kind')!='reviewer' or health.get('runtime_version')!=control['runtime_version']:
        raise ValueError('候选运行版本不一致；不会打开旧版。')
    listener=subprocess.run(['/usr/sbin/lsof','-a','-p',str(control['pid']),'-iTCP:'+str(parsed.port),'-sTCP:LISTEN','-n','-P','-Fpn'],check=True,capture_output=True,text=True,timeout=5).stdout.splitlines()
    if 'p'+str(control['pid']) not in listener or 'n127.0.0.1:'+str(parsed.port) not in listener:
        raise ValueError('候选端口与启动进程不匹配。')
    content=urlopen(url+'app.js',timeout=5).read()
    if hashlib.sha256(content).hexdigest()!=control['app_js_sha256']:
        raise ValueError('页面资源与最新候选不一致；不会打开旧版。')
    return url,control['release_commit']


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--control',type=Path,required=True);p.add_argument('--check',action='store_true');args=p.parse_args()
    url,commit=checked_url(args.control)
    if not args.check:subprocess.run(['/usr/bin/open',url],check=True)
    print('最新候选 '+commit[:7]+' 已核对；'+('未打开页面，未提交问题。' if args.check else '已打开本机真实四源试用页面。'))


if __name__=='__main__':main()
