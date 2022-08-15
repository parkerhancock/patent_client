from dataclasses import dataclass

from patent_client.util.base.collections import ListManager
from patent_client.util.base.related import get_model

from ..model import Image
from ..model import Publication
from ..model import PublicationResult


@dataclass
class PatentResult(PublicationResult):
    @property
    def publication(self) -> "patent_client.uspto.fulltext.patent.model.Patent":
        return get_model("patent_client.uspto.fulltext.patent.model.Patent").objects.get(
            publication_number=self.publication_number
        )


@dataclass
class Patent(Publication):
    __manager__ = "patent_client.uspto.fulltext.patent.manager.PatentManager"

    @property
    def forward_citations(self) -> "ListManager[patent_client.uspto.fulltext.patent.model.Patent]":
        return get_model("patent_client.uspto.fulltext.patent.model.Patent").objects.filter(
            referenced_by=self.publication_number
        )

    @property
    def images(self) -> "patent_client.uspto.fulltext.patent.model.PatentImage":
        return get_model("patent_client.uspto.fulltext.patent.model.PatentImage").objects.get(pdf_url=self.pdf_url)

    def __repr__(self):
        return f"{self.__class__.__name__}(publication_number={self.publication_number}, publication_date={self.publication_date.isoformat()}, title={self.title})"


@dataclass
class PatentImage(Image):
    __manager__ = "patent_client.uspto.fulltext.patent.manager.PatentImageManager"
