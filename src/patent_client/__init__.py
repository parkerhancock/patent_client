# flake8: noqa
import time

start = time.time()
from pathlib import Path
from .version import __version__
from .settings import load_settings, DEFAULT_SETTINGS

SETTINGS = load_settings()

import colorlog
import logging
import logging.handlers

LOG_FILENAME = Path(SETTINGS.DEFAULT.BASE_DIR).expanduser() / SETTINGS.DEFAULT.LOG_FILE

# Set up a specific logger with our desired output level
logger = logging.getLogger()
logger.setLevel(SETTINGS.DEFAULT.LOG_LEVEL)


# Add the log message handler to the logger
handler = logging.FileHandler(LOG_FILENAME)
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s"))

logger = colorlog.getLogger()
logger.addHandler(handler)

logger.info(f"Starting Patent Client with log level {SETTINGS.DEFAULT.LOG_LEVEL}")

from .session import PatentClientSession  # isort:skip
from .util.datetime.date_parse import parse_duration  # isort:skip

session = PatentClientSession()
session.remove_expired_responses(expire_after=parse_duration(SETTINGS.CACHE.MAX_AGE))

from patent_client.epo.published.model import Inpadoc  # isort:skip

# from patent_client.usitc.model import ITCAttachment
# from patent_client.usitc.model import ITCDocument
# from patent_client.usitc.model import ITCInvestigation
from patent_client.uspto.assignment.model import Assignment  # isort:skip
from patent_client.uspto.fulltext.patent.model import Patent  # isort:skip
from patent_client.uspto.fulltext.published_application.model import (
    PublishedApplication,
)  # isort:skip
from patent_client.uspto.peds.model import USApplication  # isort:skip
from patent_client.uspto.ptab.model import PtabDecision  # isort:skip
from patent_client.uspto.ptab.model import PtabDocument  # isort:skip
from patent_client.uspto.ptab.model import PtabProceeding  # isort:skip

elapsed = time.time() - start
logger.debug(f"Startup Complete!, took {elapsed:.3f} seconds")
