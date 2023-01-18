import datetime
from dataclasses import dataclass
from dataclasses import field

from patent_client.epo.ops.number_service.model import DocumentId
from patent_client.util import Model
from yankee.data import ListCollection


@dataclass
class MetaData(Model):
    status_of_data: str = None
    docdb_publication_number: str = None
    subscriber_exchange_date: "datetime.date" = None
    epo_created_date: "datetime.date" = None
    docdb_integer: int = None


@dataclass
class LegalEvent(Model):
    """
    Field descriptions are here:
    https://documents.epo.org/projects/babylon/eponot.nsf/0/EF223017D933B30AC1257B50005A042E/$File/14.11_User_Documentation_3.1_en.pdf

    """

    filing_or_publication: str = None
    document_number: str = None
    ip_type: str = None
    metadata: MetaData = None
    country_code: str = None
    text_record: str = None

    event_date: "datetime.date" = None
    event_code: str = None
    event_country: str = None
    event_description: str = None
    regional_event_code: str = None

    corresponding_patent: str = None
    corresponding_patent_publication_date: "datetime.date" = None

    designated_states: str = None
    extension_name: str = None
    new_owner_name: str = None
    free_text: str = None
    spc_number: str = None
    spc_filing_date: str = None
    expiry: str = None
    publication_language: str = None
    inventor_name: str = None
    ipc_class: str = None
    representative_name: str = None
    payment_date: str = None
    opponent_name: str = None
    year_of_fee_payment: str = None
    name_of_requester: str = None
    date_extension_granted: str = None
    extension_states: str = None
    effective_date: "datetime.date" = None
    date_of_withdrawal: str = None

    def __repr__(self):
        return f"Event(document_number={self.document_number}, event_description={self.event_description}, event_date={self.event_date})"


@dataclass
class Legal(Model):
    __manager__ = "patent_client.epo.ops.legal.manager.LegalManager"
    publication_reference: "DocumentId" = None
    events: list = field(default_factory=ListCollection)
