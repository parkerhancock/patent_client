from dataclasses import dataclass
from dataclasses import field
from typing import List

from patent_client.epo.ops.number_service.model import DocumentId
from patent_client.util import Model


@dataclass
class PriorityClaim(Model):
    application_number: str = None
    application_reference: DocumentId = None
    sequence: int = None
    kind: str = None
    active: bool = None


@dataclass
class FamilyMember(Model):
    publication_number: str = None
    application_number: str = None
    family_id: str = None
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
    publication_reference: DocumentId = None
    num_records: int = None
    publication_number: str = None
    family_members: List[FamilyMember] = field(default_factory=list)
