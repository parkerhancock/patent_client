# flake8: noqa
# nopycln: file
import time

from .version import __version__  # noqa

start = time.time()
from pathlib import Path
from .settings import load_settings

SETTINGS = load_settings()

import logging
import logging.handlers

# Revert base directory to local if there's an access problem

BASE_DIR = Path(SETTINGS.DEFAULT.BASE_DIR).expanduser()
try:
    BASE_DIR.mkdir(exist_ok=True, parents=True)
except OSError:
    BASE_DIR = Path(__file__).parent.parent.parent / "_build"
    BASE_DIR.mkdir(exist_ok=True, parents=True)
    SETTINGS.DEFAULT.BASE_DIR = str(BASE_DIR)

LOG_FILENAME = BASE_DIR / SETTINGS.DEFAULT.LOG_FILE

# Set up a specific logger with our desired output level
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.DEFAULT.LOG_LEVEL)


# Add the log message handler to the logger
handler = logging.FileHandler(LOG_FILENAME)
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)

logger.info(f"Starting Patent Client with log level {SETTINGS.DEFAULT.LOG_LEVEL}")

from .session import PatentClientSession  # isort:skip

session = PatentClientSession()
# session.remove_expired_responses(expire_after=parse_duration(SETTINGS.CACHE.MAX_AGE))

# Set up yankee
import yankee

yankee.use_model = True


from patent_client.epo.ops.published.model import Inpadoc  # isort:skip

# from patent_client.usitc.model import ITCAttachment
# from patent_client.usitc.model import ITCDocument
# from patent_client.usitc.model import ITCInvestigation
from patent_client.uspto.assignment.model import Assignment  # isort:skip
from patent_client.uspto.peds.model import USApplication  # isort:skip
from patent_client.uspto.ptab.model import PtabDecision  # isort:skip
from patent_client.uspto.ptab.model import PtabDocument  # isort:skip
from patent_client.uspto.ptab.model import PtabProceeding  # isort:skip
from patent_client.uspto.global_dossier.model import GlobalDossier, GlobalDossierApplication  # isort:skip
from patent_client.uspto.public_search.model import (
    PublicSearch,
    PublicSearchDocument,
    Patent,
    PatentBiblio,
    PublishedApplication,
    PublishedApplicationBiblio,
)  # isort:skip

elapsed = time.time() - start
logger.debug(f"Startup Complete!, took {elapsed:.3f} seconds")

__all__ = [
    "Inpadoc",
    "Assignment",
    "PublicSearch",
    "PublicSearchDocument",
    "Patent",
    "PatentBiblio",
    "PublishedApplication",
    "PublishedApplicationBiblio",
    "USApplication",
    "PtabDecision",
    "PtabDocument",
    "PtabProceeding",
    "GlobalDossier",
]
