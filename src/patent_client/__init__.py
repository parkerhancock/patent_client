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
CACHE_CONFIG = dict(
    expire_after=cache_max_age,
    backend=requests_cache.backends.sqlite.DbCache(
        location=str(CACHE_BASE / "requests_cache")
    ),
    allowable_methods=("GET", "POST"),
    )

session = requests_cache.CachedSession(**CACHE_CONFIG)
session.cache.remove_old_entries(datetime.datetime.utcnow() - cache_max_age)
session.headers["User-Agent"] = f"Python Patent Clientbot/{__version__} (pypatent2018@gmail.com)"

SETTINGS_FILE = Path("~/.iprc").expanduser()
if not SETTINGS_FILE.exists():
    DEFAULT_SETTINGS = Path(__file__).parent / "default_settings.json"
    shutil.copy(str(DEFAULT_SETTINGS), SETTINGS_FILE)

SETTINGS = json.load(open(SETTINGS_FILE))

from patent_client.epo.inpadoc import Inpadoc  # isort:skip
from patent_client.usitc.edis import ITCInvestigation, ITCDocument, ITCAttachment
from patent_client.uspto.ptab import PtabProceeding, PtabDocument, PtabDecision
from patent_client.uspto.assignment import Assignment
from patent_client.uspto.peds import USApplication
