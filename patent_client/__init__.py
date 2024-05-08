# flake8: noqa
# nopycln: file
import time

import patent_client.patches  # noqa # Run patching code

from .version import __version__  # noqa

start = time.time()

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

try:
    from ._sync import *
except ImportError:
    pass

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
