from .biblio import PublicSearchBiblio, PublicSearchBiblioPage
from .document import PublicSearchDocument


class PatentBiblio(PublicSearchBiblio):
    pass


class Patent(PublicSearchDocument):
    pass


class PublishedApplicationBiblio(PublicSearchBiblio):
    pass


class PublishedApplication(PublicSearchDocument):
    pass


__all__ = [
    "PatentBiblio",
    "Patent",
    "PublishedApplicationBiblio",
    "PublishedApplication",
    "PublicSearchBiblio",
    "PublicSearchBiblioPage",
    "PublicSearchDocument",
    "PublicSearchDocument",
]
