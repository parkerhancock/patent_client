from dataclasses import dataclass
from typing import List, Union, Optional
import datetime
from patent_client.util import Model, one_to_many, one_to_one

@dataclass
class PtabProceeding(Model):
    __manager__ = 'patent_client.uspto.ptab.manager.PtabProceedingManager'
    subproceeding_type_category: str
    proceeding_number: str
    proceeding_status_category: str
    proceeding_type_category: str

    # Party Information
    appl_id: str
    respondent_party_name: str
    petitioner_counsel_name: Optional[str] = None 
    petitioner_party_name: Optional[str] = None
    respondent_counsel_name: Optional[str] = None
    respondent_patent_owner_name: Optional[str] = None

    # Application Information
    inventor: Optional[str] = None
    patent_number: Optional[str] = None
    respondent_technology_center_number: Optional[str] = None
    respondent_grant_date: Optional[datetime.date] = None
    accorded_filing_date: Optional[datetime.date] = None
    decision_date: Optional[datetime.date] = None
    institution_decision_date: Optional[datetime.date] = None
    proceeding_filing_date: Optional[datetime.date] = None

    documents = one_to_many('patent_client.uspto.ptab.PtabDocument', proceeding_number='proceeding_number')
    decisions = one_to_many('patent_client.uspto.ptab.PtabDecision', proceeding_number='proceeding_number')

@dataclass
class PtabDocument(Model):
    __manager__ = 'patent_client.uspto.ptab.manager.PtabDocumentManager'
    document_identifier: str
    document_category: str
    document_type_name: str
    document_number: int
    document_name: str
    document_filing_date: datetime.date
    proceeding_number: str
    proceeding_type_category: str
    title: Optional[str] = None

    proceeding = one_to_one('patent_client.uspto.ptab.PtabProceeding', proceeding_number='proceeding_number')

@dataclass
class PtabDecision(Model):
    __manager__ = 'patent_client.uspto.ptab.manager.PtabDecisionManager' 
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
    proceeding = one_to_one('patent_client.uspto.ptab.PtabProceeding', proceeding_number='proceeding_number')


