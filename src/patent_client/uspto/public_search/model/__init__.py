from .biblio import PublicSearchBiblio
from .biblio import PublicSearchBiblioPage
from .document import PublicSearchDocument


class PatentBiblio(PublicSearchBiblio):
    pass


class Patent(PublicSearchDocument):
    pass


class PublishedApplicationBiblio(PublicSearchBiblio):
    pass


class PublishedApplication(PublicSearchDocument):
    pass
