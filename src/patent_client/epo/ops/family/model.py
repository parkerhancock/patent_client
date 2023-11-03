from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional

from patent_client.epo.ops.number_service.model import DocumentId
from patent_client.util import Model


@dataclass
class PriorityClaim(Model):
    application_number: Optional[str] = None
    application_reference: Optional[DocumentId] = None
    sequence: Optional[int] = None
    kind: Optional[str] = None
    active: Optional[bool] = None


@dataclass
class FamilyMember(Model):
    publication_number: Optional[str] = None
    application_number: Optional[str] = None
    family_id: Optional[str] = None
    publication_reference: list = field(default_factory=list)
    application_reference: list = field(default_factory=list)
    priority_claims: List[PriorityClaim] = field(default_factory=list)

    @property
    def docdb_number(self):
        return self.publication_number

    def __repr__(self):
        return f"FamilyMember(publication_number={self.publication_number})"


@dataclass
class Family(Model):
    __manager__ = "patent_client.epo.ops.family.manager.FamilyManager"
    publication_reference: Optional[DocumentId] = None
    num_records: Optional[int] = None
    publication_number: Optional[str] = None
    family_members: List[FamilyMember] = field(default_factory=list)
