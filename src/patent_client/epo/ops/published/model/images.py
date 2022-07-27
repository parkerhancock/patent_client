from dataclasses import dataclass, field

from patent_client.util import Model

from patent_client.epo.ops.number_service.model import DocumentId

@dataclass
class Section(Model):
    name: str = None
    start_page: str = None

@dataclass
class ImageDocument(Model):
    num_pages: int = None
    description: str = None
    link: str = None
    formats: list = field(default_factory=list)
    sections: list = field(default_factory=list)

@dataclass
class Images(Model):
    search_reference: DocumentId = None
    publication_reference: DocumentId = None
    documents: list = field(default_factory=list)

