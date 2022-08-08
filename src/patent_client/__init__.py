# flake8: noqa
__version__ = "3.0.0"

from .version import __version__
from .settings import load_settings, DEFAULT_SETTINGS

SETTINGS = load_settings()

from .session import PatentClientSession

session = PatentClientSession()

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
"""
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
"""
