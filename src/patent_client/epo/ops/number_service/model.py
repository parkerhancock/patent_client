import datetime
from dataclasses import dataclass
from dataclasses import field
from typing import Optional

from patent_client.util.base.model import Model


@dataclass
class DocumentId(Model):
    doc_type: Optional[str] = None
    id_type: Optional[str] = None
    country: Optional[str] = None
    number: Optional[str] = None
    kind: Optional[str] = None
    date: Optional[datetime.date] = None
    name: Optional[str] = None

    def __str__(self):
        return f"{self.country}{self.number}{self.kind}"


@dataclass
class NumberServiceResult(Model):
    input_doc: DocumentId
    output_doc: DocumentId
    service_version: Optional[str] = None
    messages: list = field(default_factory=list)
