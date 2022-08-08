from dataclasses import dataclass

from patent_client.util import Model
from patent_client.util import one_to_many
from patent_client.util import one_to_one

from ..model import Image
from ..model import Publication
from ..model import PublicationResult


@dataclass
class PublishedApplicationResult(PublicationResult):
    publication = one_to_one(
        "patent_client.uspto.fulltext.published_application.model.PublishedApplication",
        publication_number="publication_number",
    )


@dataclass
class PublishedApplication(Publication):
    __manager__ = "patent_client.uspto.fulltext.published_application.manager.PublishedApplicationManager"
    forward_citations = one_to_many(
        "patent_client.uspto.fulltext.patent.model.Patent",
        referenced_by="publication_number",
    )
    images = one_to_one(
        "patent_client.uspto.fulltext.published_application.model.PublishedApplicationImage",
        pdf_url="pdf_url",
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(publication_number={self.publication_number}, publication_date={self.publication_date.isoformat()}, title={self.title})"


@dataclass
class PublishedApplicationImage(Image):
    __manager__ = "patent_client.uspto.fulltext.published_application.manager.PublishedApplicationImageManager"
