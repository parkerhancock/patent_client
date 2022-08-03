# flake8: noqa
__version__ = "2.2.1"

import datetime
import json
import shutil
from pathlib import Path

import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set Up Requests Cache
cache_max_age = datetime.timedelta(days=3)
cache_dir = "~/.patent_client"
CACHE_BASE = Path(cache_dir).expanduser()
CACHE_BASE.mkdir(exist_ok=True)
CACHE_CONFIG = dict(
    expire_after=cache_max_age,
    db_path=str(CACHE_BASE / "requests_cache"),
    backend="sqlite",
    allowable_methods=("GET", "POST"),
    ignored_parameters=[
        "Authorization",
    ],
)

session = requests_cache.CachedSession(**CACHE_CONFIG)
session.remove_expired_responses(expire_after=cache_max_age)
session.headers["User-Agent"] = f"Python Patent Clientbot/{__version__} (parkerhancock@users.noreply.github.com)"

# Install a default retry on the session using urrlib3
retry = Retry(total=5, backoff_factor=0.2)
session.mount("https://", HTTPAdapter(max_retries=retry))
session.mount("http://", HTTPAdapter(max_retries=retry))

SETTINGS_FILE = Path("~/.iprc").expanduser()
if not SETTINGS_FILE.exists():
    DEFAULT_SETTINGS = Path(__file__).parent / "default_settings.json"
    shutil.copy(str(DEFAULT_SETTINGS), SETTINGS_FILE)

SETTINGS = json.load(open(SETTINGS_FILE))

from patent_client.epo.published.model import Inpadoc  # isort:skip
# from patent_client.usitc.model import ITCAttachment
# from patent_client.usitc.model import ITCDocument
# from patent_client.usitc.model import ITCInvestigation
from patent_client.uspto.assignment.model import Assignment # isort:skip
# from patent_client.uspto.fulltext.patent.model import Patent
# from patent_client.uspto.fulltext.published_application.model import PublishedApplication
from patent_client.uspto.peds.model import USApplication # isort:skip
# from patent_client.uspto.ptab.model import PtabDecision
# from patent_client.uspto.ptab.model import PtabDocument
# from patent_client.uspto.ptab.model import PtabProceeding

import logging
import logging.handlers

LOG_FILENAME = "cloud_patent.log"

# Set up a specific logger with our desired output level
logger = logging.getLogger()
logger.setLevel("INFO")


# Add the log message handler to the logger
handler = logging.FileHandler(LOG_FILENAME)
logger.addHandler(handler)


import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s"))

logger = colorlog.getLogger()
logger.addHandler(handler)
