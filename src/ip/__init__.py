__version__ = "0.1.0"

import json
import shutil
import os
import time
from pathlib import Path

CACHE_BASE = Path("~/.ip").expanduser()
CACHE_BASE.mkdir(exist_ok=True)
CACHE_MAX_AGE = 60 * 60 * 24 * 7  # 1 week
now = time.time()
# Clear old files out of cache
for path, folders, files in os.walk(CACHE_BASE):
    for f in files:
        fname = os.path.join(path, f)
        if now - os.path.getmtime(fname) > CACHE_MAX_AGE:
            os.remove(fname)

SETTINGS_FILE = Path("~/.iprc").expanduser()
if not SETTINGS_FILE.exists():
    DEFAULT_SETTINGS = Path(__file__).parent / "default_settings.json"
    shutil.copy(str(DEFAULT_SETTINGS), SETTINGS_FILE)

SETTINGS = json.load(open(SETTINGS_FILE))

from ip.epo_ops import Inpadoc, Epo
from ip.uspto_assignments import Assignment
from ip.uspto_exam_data import USApplication
from ip.uspto_ptab import PtabDocument, PtabTrial