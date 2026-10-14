#!/usr/bin/env python3
"""User-invoked local page entry; never an automated browser test."""
import subprocess,sys
from pathlib import Path

root=Path(__file__).resolve().parent

def main():
    from scripts.local_entry import renew,entry_url
    if '--check' in sys.argv:
        renew(root,check_only=True)
        print('入口实例检查通过；双击可打开当前登录入口。未打开浏览器，未提交问题。')
        return
    token=renew(root)
    if '--refresh-only' in sys.argv:
        print('本机登录入口已准备；未打开浏览器，未提交问题。')
        return
    subprocess.run(['/usr/bin/open',entry_url(root)+('#ticket='+token if token else '')],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    print('页面已交给默认浏览器打开。登录码不会显示在终端。')

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(str(error) if isinstance(error,ValueError) else '页面暂时无法打开。请在聊天中让我检查入口。')
        if '--check' not in sys.argv and '--refresh-only' not in sys.argv:input('按回车关闭窗口。')
        sys.exit(1)
