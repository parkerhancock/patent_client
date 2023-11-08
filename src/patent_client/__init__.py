# flake8: noqa
# nopycln: file
import time

from .version import __version__  # noqa

start = time.time()

import nest_asyncio

nest_asyncio.apply()

from pathlib import Path
from .settings import Settings

SETTINGS = Settings()


import logging
import logging.handlers

# Revert base directory to local if there's an access problem

BASE_DIR = SETTINGS.base_dir
try:
    BASE_DIR.mkdir(exist_ok=True, parents=True)
except OSError:
    BASE_DIR = Path(__file__).parent.parent.parent / "_build"
    BASE_DIR.mkdir(exist_ok=True, parents=True)
    SETTINGS.DEFAULT.BASE_DIR = str(BASE_DIR)

LOG_FILENAME = BASE_DIR / SETTINGS.log_file
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True, parents=True)

# Set up a specific logger with our desired output level
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.log_level)


# Add the log message handler to the logger
handler = logging.FileHandler(LOG_FILENAME)
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)

logger.info(f"Starting Patent Client with log level {SETTINGS.log_level}")


from patent_client.epo.ops.published.model import Inpadoc  # isort:skip

# from patent_client.usitc.model import ITCAttachment
# from patent_client.usitc.model import ITCDocument
# from patent_client.usitc.model import ITCInvestigation
from patent_client.uspto.assignment.model import Assignment  # isort:skip

from patent_client.uspto.peds import USApplication  # isort:skip

from patent_client.uspto.ptab.model import PtabDecision  # isort:skip
from patent_client.uspto.ptab.model import PtabDocument  # isort:skip
from patent_client.uspto.ptab.model import PtabProceeding  # isort:skip
from patent_client.uspto.global_dossier.model import (
    GlobalDossier,
    GlobalDossierApplication,
)  # isort:skip

# from patent_client.uspto.public_search.model import (
#    PublicSearch,
#    PublicSearchDocument,
#    Patent,
#    PatentBiblio,
#    PublishedApplication,
#    PublishedApplicationBiblio,
# )  # isort:skip

elapsed = time.time() - start
logger.info(f"Startup Complete!, took {elapsed:.3f} seconds")

cache_dir = Path("~/.patent_client/cache").expanduser()
cache_dir.parent.mkdir(exist_ok=True, parents=True)

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
