from dataclasses import dataclass, field
from patent_client.util import Model
from patent_client.epo.ops.number_service.model import DocumentId

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
    priority_claims: list = field(default_factory=list)

@dataclass
class Family(Model):
    publication_reference: DocumentId = None
    num_records: int = None
    publication_number: str = None
    family_members: list = field(default_factory=list)