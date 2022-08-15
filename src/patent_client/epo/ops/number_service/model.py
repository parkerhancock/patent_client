import datetime
from dataclasses import dataclass
from dataclasses import field

from patent_client.util.base.model import Model


@dataclass
class DocumentId(Model):
    doc_type: str = None
    id_type: str = None
    country: str = None
    number: str = None
    kind: str = None
    date: "datetime.date" = None
    name: str = None

    def __str__(self):
        return f"{self.country}{self.number}{self.kind}"


@dataclass
class NumberServiceResult(Model):
    input_doc: DocumentId
    output_doc: DocumentId
    service_version: str = None
    messages: list = field(default_factory=list)
