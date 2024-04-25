from typing import List, Optional

from pydantic import Field

from patent_client.util.claims.model import Claim

from ...util import EpoBaseModel
from ..schema.fulltext import ClaimsSchema, DescriptionSchema


class FTDocumentId(EpoBaseModel):
    country: Optional[str] = None
    doc_number: Optional[str] = None
    kind: Optional[str] = None

    def __str__(self):
        return f"{self.country}{self.doc_number}{self.kind}"


class Claims(EpoBaseModel):
    __schema__ = ClaimsSchema()
    document_id: Optional[FTDocumentId] = None
    claims: List[Claim] = Field(default_factory=list)
    claim_text: Optional[str] = None

    @property
    def docdb_number(self) -> str:
        return str(self.document_id)

    def __repr__(self):
        return f"Claims(document_id={str(self.document_id)})"


class Description(EpoBaseModel):
    __schema__ = DescriptionSchema()
    document_id: Optional[FTDocumentId] = None
    description: Optional[str] = None

    @property
    def docdb_number(self) -> str:
        return str(self.document_id)
