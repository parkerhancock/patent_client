from typing import List
from dataclasses import dataclass, field

from patent_client.util import Model

from patent_client.util.claims.model import Claim

@dataclass
class FTDocumentId(Model):
    country: str = None
    doc_number: str = None
    kind: str = None

@dataclass
class Claims(Model):
    __manager__ = "patent_client.epo.ops.published.manager.ClaimsManager"
    document_id: FTDocumentId
    claims: List[Claim] = field(default_factory=list)
    claim_text: str = None

@dataclass
class Description(Model):
    __manager__ = "patent_client.epo.ops.published.manager.DescriptionManager"
    document_id: FTDocumentId = None
    description: str = None