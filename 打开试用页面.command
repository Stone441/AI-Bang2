#!/usr/bin/env python3
"""User-invoked local page entry; never an automated browser test."""
import json,re,stat,subprocess,sys,time
from pathlib import Path
from urllib.request import urlopen

root=Path(__file__).resolve().parent
token_file=root/'.runtime/page-failure-ux-logs/human-bootstrap-token'

def main():
    if not token_file.is_file() or token_file.is_symlink():
        raise ValueError('登录入口尚未准备好。请在聊天中让我刷新入口。')
    if stat.S_IMODE(token_file.stat().st_mode)!=0o600:
        raise ValueError('登录码文件权限不符合要求。请在聊天中让我检查入口。')
    if time.time()-token_file.stat().st_mtime>540:
        raise ValueError('一次性入口已过期。请在聊天中回复“刷新入口”。')
    with urlopen('http://127.0.0.1:49161/api/health',timeout=5) as response:
        health=json.load(response)
    if health.get('auth_kind')!='operator':
        raise ValueError('当前端口不是预期的本机试用服务。请让我检查。')
    token=token_file.read_text().strip()
    if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}',token):
        raise ValueError('登录码格式异常。请让我检查入口。')
    if '--check' in sys.argv:
        print('入口检查通过；未打开浏览器，未提交问题。')
        return
    subprocess.run(['/usr/bin/open','http://127.0.0.1:49161/#ticket='+token],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    print('页面已交给默认浏览器打开。登录码不会显示在终端。')

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(str(error) if isinstance(error,ValueError) else '页面暂时无法打开。请在聊天中让我检查入口。')
        if '--check' not in sys.argv:input('按回车关闭窗口。')
        sys.exit(1)
