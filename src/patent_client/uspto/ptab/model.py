import datetime
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import Union

from patent_client.util import Model
from patent_client.util import one_to_many
from patent_client.util import one_to_one


@dataclass
class PtabProceeding(Model):
    """A PTAB Proceeding - e.g. IPR/CBM/DER Trial, Patent Appeal, Interference, etc.

    All fields are query-able. Date ranges can be formed by inserting "from" or "to" on a query
    for a date range.

    """

    __manager__ = "patent_client.uspto.ptab.manager.PtabProceedingManager"
    subproceeding_type_category: str
    proceeding_number: str
    proceeding_status_category: str
    proceeding_type_category: str

    # Party Information
    appl_id: str = field(repr=False)
    respondent_party_name: str = field(default=None)
    petitioner_counsel_name: Optional[str] = field(default=None, repr=False)
    petitioner_party_name: Optional[str] = field(default=None, repr=False)
    respondent_counsel_name: Optional[str] = field(default=None, repr=False)
    respondent_patent_owner_name: Optional[str] = field(default=None, repr=False)

    # Application Information
    inventor: Optional[str] = field(default=None, repr=False)
    patent_number: Optional[str] = field(default=None, repr=False)
    respondent_technology_center_number: Optional[str] = field(default=None, repr=False)
    respondent_grant_date: Optional[datetime.date] = field(default=None, repr=False)
    accorded_filing_date: Optional[datetime.date] = field(default=None, repr=False)
    decision_date: Optional[datetime.date] = field(default=None, repr=False)
    institution_decision_date: Optional[datetime.date] = field(default=None, repr=False)
    proceeding_filing_date: Optional[datetime.date] = field(default=None, repr=False)

    documents = one_to_many(
        "patent_client.uspto.ptab.PtabDocument", proceeding_number="proceeding_number"
    )
    """Documents associated with the Proceeding"""
    decisions = one_to_many(
        "patent_client.uspto.ptab.PtabDecision", proceeding_number="proceeding_number"
    )
    """Decisions associated with the Proceeding"""
    us_application = one_to_one(
        "patent_client.uspto.peds.Application", appl_id="appl_id"
    )
    """The US Application provided by PEDS associated with the Proceeding"""


@dataclass
class PtabDocument(Model):
    __manager__ = "patent_client.uspto.ptab.manager.PtabDocumentManager"
    document_identifier: str = field(repr=False)
    document_category: str
    document_type_name: str
    document_number: int
    document_name: str
    document_filing_date: datetime.date
    proceeding_number: str = field(repr=False)
    proceeding_type_category: str = field(repr=False)
    title: Optional[str] = None

    proceeding = one_to_one(
        "patent_client.uspto.ptab.PtabProceeding", proceeding_number="proceeding_number"
    )
    """The PTAB proceeding associated with the document"""


@dataclass
class PtabDecision(Model):
    __manager__ = "patent_client.uspto.ptab.manager.PtabDecisionManager"
    proceeding_number: str
    board_rulings: List[str]
    decision_type_category: str
    document_identifier: str
    document_name: str
    identifier: str
    subdecision_type_category: str
    issue_type: Optional[str] = None
    object_uu_id: Optional[str] = None
    petitioner_technology_center_number: Optional[str] = None

    proceeding = one_to_one(
        "patent_client.uspto.ptab.PtabProceeding", proceeding_number="proceeding_number"
    )
    """The PTAB proceeding associated with the document"""
