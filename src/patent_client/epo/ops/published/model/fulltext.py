from dataclasses import dataclass, field

from patent_client.util import Model

@dataclass
class FTDocumentId(Model):
    country: str = None
    doc_number: str = None
    kind: str = None

@dataclass
class Claims(Model):
    document_id: FTDocumentId
    claims: list = field(default_factory=list)

@dataclass
class Description(Model):
    document_id: FTDocumentId = None
    description: str = None