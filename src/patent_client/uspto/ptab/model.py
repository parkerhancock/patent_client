import datetime
from dataclasses import dataclass
from dataclasses import field

from patent_client.util import Model
from patent_client.util import one_to_many
from patent_client.util import one_to_one


@dataclass
class AdditionalRespondent(Model):
    application_number_text: str = None
    inventor_name: str = None
    patent_number: str = None
    party_name: str = None


@dataclass
class PtabProceeding(Model):
    """A PTAB Proceeding - e.g. IPR/CBM/DER Trial, Patent Appeal, Interference, etc.

    All fields are query-able. Date ranges can be formed by inserting "from" or "to" on a query
    for a date range.

    """

    __manager__ = "patent_client.uspto.ptab.manager.PtabProceedingManager"
    # Proceeding Metadata
    last_modified_date: "datetime.datetime" = None
    last_modified_user_id: "datetime.datetime" = None
    institution_decision_date: "datetime.date" = None
    proceeding_filing_date: "datetime.date" = None
    accorded_filing_date: "datetime.date" = None
    proceeding_status_category: str = None
    proceeding_number: str = None
    proceeding_last_modified_date: "datetime.date" = None
    proceeding_type_category: str = None
    subproceeding_type_category: str = None
    decision_date: "datetime.date" = None
    docket_notice_mail_date: "datetime.date" = None
    declaration_date: "datetime.date" = None
    style_name_text: str = None

    # Respondent Information
    respondent_technology_center_number: str = None
    respondent_patent_owner_name: str = None
    respondent_party_name: str = None
    respondent_group_art_unit_number: str = None
    respondent_inventor_name: str = None
    respondent_counsel_name: str = None
    respondent_grant_date: "datetime.date" = None
    respondent_patent_number: str = None
    respondent_application_number_text: str = None
    respondent_publication_number: str = None
    respondent_publication_date: "datetime.date" = None

    # Petitioner Information
    petitioner_technology_center_number: str = None
    petitioner_patent_owner_name: str = None
    petitioner_party_name: str = None
    petitioner_group_art_unit_number: str = None
    petitioner_inventor_name: str = None
    petitioner_counsel_name: str = None
    petitioner_grant_date: "datetime.date" = None
    petitioner_patent_number: str = None
    petitioner_application_number_text: str = None

    # Appellant Information
    appellant_technology_center_number: str = None
    appellant_patent_owner_name: str = None
    appellant_party_name: str = None
    appellant_group_art_unit_number: str = None
    appellant_inventor_name: str = None
    appellant_counsel_name: str = None
    appellant_grant_date: "datetime.date" = None
    appellant_patent_number: str = None
    appellant_application_number_text: str = None
    appellant_publication_date: "datetime.date" = None
    appellant_publication_number: str = None
    third_party_name: str = None

    # Second Respondent (if any)
    second_respondent_party_name: str = None
    second_respondent_appl_number_text: str = None
    second_respondent_patent_number: str = None
    second_respondent_grant_date: "datetime.date" = None
    second_respondent_patent_owner_name: str = None
    second_respondent_inventor_name: str = None
    second_respondent_counsel_name: str = None
    second_respondent_g_a_u_number: str = None
    second_respondent_tech_center_number: str = None
    second_respondent_pub_number: str = None
    second_respondent_publication_date: "datetime.date" = None

    additional_respondents: "List" = field(default_factory=list)

    documents = one_to_many("patent_client.uspto.ptab.PtabDocument", proceeding_number="proceeding_number")
    """Documents associated with the Proceeding"""
    decisions = one_to_many("patent_client.uspto.ptab.PtabDecision", proceeding_number="proceeding_number")
    """Decisions associated with the Proceeding"""
    us_application = one_to_one("patent_client.uspto.peds.Application", appl_id="appl_id")
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
    title: "Optional[str]" = None

    proceeding = one_to_one("patent_client.uspto.ptab.PtabProceeding", proceeding_number="proceeding_number")
    """The PTAB proceeding associated with the document"""


@dataclass
class PtabDecision(Model):
    __manager__ = "patent_client.uspto.ptab.manager.PtabDecisionManager"
    proceeding_number: str
    board_rulings: "List[str]"
    decision_type_category: str
    document_identifier: str
    document_name: str
    identifier: str
    subdecision_type_category: str
    issue_type: "Optional[str]" = None
    object_uu_id: "Optional[str]" = None
    petitioner_technology_center_number: "Optional[str]" = None

    proceeding = one_to_one("patent_client.uspto.ptab.PtabProceeding", proceeding_number="proceeding_number")
    """The PTAB proceeding associated with the document"""
