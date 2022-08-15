from .patent.model import Patent
from .published_application.model import PublishedApplication
__api_name__ = "USPTO Fulltext Databases"

__all__ = [
    "Patent",
    "PublishedApplication",
]
