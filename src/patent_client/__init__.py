# flake8: noqa
__version__ = "1.1.4"

import json
import os
import sys
import platform
import shutil
import time
from pathlib import Path

import requests_cache
import datetime


# Set Up Requests Cache
cache_max_age = datetime.timedelta(days=3)
cache_dir = "~/.patent_client"


CACHE_BASE = Path(cache_dir).expanduser()
CACHE_BASE.mkdir(exist_ok=True)
session = requests_cache.CachedSession(
    expire_after=cache_max_age,
    backend=requests_cache.backends.sqlite.DbCache(
        location=str(CACHE_BASE / "requests_cache")
    )
)
session.cache.remove_old_entries(datetime.datetime.utcnow() - cache_max_age)
#print(f"python patent_client-v.{__version__}(Python-v{sys.version};OS{platform.platform()})(pypatent2018@gmail.com)")
session.headers["User-Agent"] = f"Python Patent Clientbot/{__version__} (pypatent2018@gmail.com)"

SETTINGS_FILE = Path("~/.iprc").expanduser()
if not SETTINGS_FILE.exists():
    DEFAULT_SETTINGS = Path(__file__).parent / "default_settings.json"
    shutil.copy(str(DEFAULT_SETTINGS), SETTINGS_FILE)

SETTINGS = json.load(open(SETTINGS_FILE))

from patent_client.epo_ops.models import Inpadoc, Epo  # isort:skip
from patent_client.uspto_assignments import Assignment  # isort:skip
from patent_client.uspto_peds import USApplication  # isort:skip
from patent_client.uspto_ptab import PtabDocument  # isort:skip
from patent_client.uspto_ptab import PtabTrial  # isort:skip
from patent_client.itc_edis import (
    ITCInvestigation,
    ITCDocument,
    ITCAttachment,
)  # isort:skip
