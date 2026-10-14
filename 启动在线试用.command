#!/usr/bin/env python3
"""User-operated dedicated ContextLedger hosting controls."""
import os,subprocess
from pathlib import Path
for suffix in ('app','tunnel'):
    label='com.kyle.contextledger.'+suffix
    domain='gui/'+str(os.getuid())
    if subprocess.run(['/bin/launchctl','print',domain+'/'+label],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
        subprocess.run(['/bin/launchctl','bootstrap',domain,str(Path.home()/'Library/LaunchAgents'/(label+'.plist'))],check=True)
print('托管进程已启动。四源检查完成后访问 https://contextledger.hellokyleshi.com')
