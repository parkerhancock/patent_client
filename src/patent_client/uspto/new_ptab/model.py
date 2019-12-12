from dataclasses import dataclass
from typing import List, Union
import datetime

@dataclass
class PtabProceeding(object):
    subproceeding_type_category: str
    proceeding_number: str
    proceeding_status_category: str
    proceeding_type_category: str

    # Party Information
    respondent_application_number_text: str
    respondent_party_name: str
    petitioner_counsel_name: str = None
    petitioner_party_name: str = None
    respondent_counsel_name: str = None
    respondent_patent_owner_name: str = None

    # Application Information
    respondent_inventor_name: str = None
    respondent_patent_number: str = None
    respondent_technology_center_number: str = None
    respondent_grant_date: datetime.date = None
    accorded_filing_date: datetime.date = None
    decision_date: datetime.date = None
    institution_decision_date: datetime.date = None
    proceeding_filing_date: datetime.date = None
    

@dataclass
class PtabDocument(object):
    document_identifier: str
    document_category: str
    document_type_name: str
    document_number: int
    document_name: str
    document_filing_date: datetime.date
    proceeding_number: str
    proceeding_type_category: str
    title: str = None

@dataclass
class PtabDecision(object):
    proceeding_number: str
    board_rulings: List[str]
    decision_type_category: str
    document_identifier: str
    document_name: str
    identifier: str
    issue_type: str
    subdecision_type_category: str
    object_uu_id: str = None
    petitioner_technology_center_number: str = None
