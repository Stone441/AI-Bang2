#!/usr/bin/env python3
"""User-operated dedicated ContextLedger hosting controls."""
import os,subprocess
from pathlib import Path
for suffix in ('tunnel','app'):
    subprocess.run(['/bin/launchctl','bootout','gui/'+str(os.getuid())+'/com.kyle.contextledger.'+suffix],check=False)
print('在线入口与本机托管应用已停止；账号、资料、审计和账本保留。')
