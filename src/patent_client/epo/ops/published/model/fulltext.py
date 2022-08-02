from dataclasses import dataclass
from dataclasses import field
from typing import List

from patent_client.epo.ops.util import InpadocModel
from patent_client.util import Model
from patent_client.util.claims.model import Claim


@dataclass
class FTDocumentId(Model):
    country: str = None
    doc_number: str = None
    kind: str = None

    def __str__(self):
        return f"{self.country}{self.doc_number}{self.kind}"


@dataclass
class Claims(Model):
    __manager__ = "patent_client.epo.ops.published.manager.ClaimsManager"
    document_id: FTDocumentId
    claims: List[Claim] = field(default_factory=list)
    claim_text: str = None

    @property
    def docdb_number(self) -> str:
        return str(self.document_id)

    def __repr__(self):
        return f"Claims(document_id={str(self.document_id)})"


@dataclass
class Description(InpadocModel):
    __manager__ = "patent_client.epo.ops.published.manager.DescriptionManager"
    document_id: FTDocumentId = None
    description: str = None

    @property
    def docdb_number(self) -> str:
        return str(self.document_id)
