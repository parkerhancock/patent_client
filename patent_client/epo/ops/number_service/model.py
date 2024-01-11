from typing import Optional

from pydantic import Field

from .schema import NumberServiceSchema
from patent_client.epo.ops.util import EpoBaseModel
from patent_client.util.pydantic_util import Date


class DocumentId(EpoBaseModel):
    doc_type: Optional[str] = None
    id_type: Optional[str] = None
    country: Optional[str] = None
    number: Optional[str] = None
    kind: Optional[str] = None
    date: Optional[Date] = None
    name: Optional[str] = None

    def __str__(self):
        return f"{self.country}{self.number}{self.kind}"


class NumberService(EpoBaseModel):
    __schema__ = NumberServiceSchema()
    input_doc: DocumentId
    output_doc: DocumentId
    service_version: Optional[str] = None
    messages: list = Field(default_factory=list)
