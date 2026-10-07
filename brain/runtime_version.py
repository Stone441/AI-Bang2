"""Nonsecret source fingerprint captured once per process, never per HTTP request.

This identifies the startup source tree, not an attestation or hot-reload signal.
Only checked-in code paths are read; runtime configuration and secrets are excluded.
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def source_fingerprint(root):
    digest = hashlib.sha256()
    for directory in ('brain', 'scripts'):
        for path in sorted((root / directory).glob('*.py')):
            digest.update(path.relative_to(root).as_posix().encode() + b'\0')
            digest.update(path.read_bytes() + b'\0')
    return digest.hexdigest()


STARTUP_SOURCE_SHA256 = source_fingerprint(Path(__file__).resolve().parents[1])
PROCESS_LOADED_AT = datetime.now(timezone.utc).isoformat()


def runtime_version():
    return {'startup_source_sha256': STARTUP_SOURCE_SHA256,
            'process_loaded_at': PROCESS_LOADED_AT,
            'meaning': 'Startup source snapshot; static UI can change independently. No hot reload.'}
