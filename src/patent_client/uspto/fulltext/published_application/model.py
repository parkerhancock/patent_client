from dataclasses import dataclass

from patent_client.util.base.collections import ListManager
from patent_client.util.base.related import get_model

from ..model import Image
from ..model import Publication
from ..model import PublicationResult


@dataclass
class PublishedApplicationResult(PublicationResult):
    @property
    def publication(self) -> "patent_client.uspto.fulltext.published_application.model.PublishedApplication":
        return get_model("patent_client.uspto.fulltext.published_application.model.PublishedApplication").objects.get(publication_number=self.publication_number)


@dataclass
class PublishedApplication(Publication):
    __manager__ = "patent_client.uspto.fulltext.published_application.manager.PublishedApplicationManager"
    @property
    def forward_citations(self) -> "ListManager[patent_client.uspto.fulltext.published_application.model.PublishedApplication]":
        return get_model("patent_client.uspto.fulltext.published_application.model.PublishedApplication").objects.filter(referenced_by=self.publication_number)

    @property
    def images(self) -> "patent_client.uspto.fulltext.published_application.model.PublishedApplicationImage":
        return get_model("patent_client.uspto.fulltext.published_application.model.PublishedApplicationImage").objects.get(pdf_url=self.pdf_url)

    def __repr__(self):
        return f"{self.__class__.__name__}(publication_number={self.publication_number}, publication_date={self.publication_date.isoformat()}, title={self.title})"


@dataclass
class PublishedApplicationImage(Image):
    __manager__ = "patent_client.uspto.fulltext.published_application.manager.PublishedApplicationImageManager"
