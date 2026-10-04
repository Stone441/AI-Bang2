"""Evidence metadata also works from a source archive without a .git directory."""
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def revision():
    try:
        return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):
        return 'unavailable-source-archive; use source_hashes'


def dirty():
    try:
        return bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip())
    except (OSError,subprocess.CalledProcessError):
        return None
