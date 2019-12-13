from dataclasses import dataclass, field, asdict, fields
from collections import OrderedDict
from typing import List, Dict, Optional
import datetime
from dateutil.relativedelta import relativedelta
from patent_client.util import one_to_many, one_to_one, Model, QuerySet

@dataclass
class Relationship(Model):
    parent_appl_id: str
    child_appl_id: str
    relationship: str
    child_app_filing_date: Optional[datetime.date] = None
    parent_app_filing_date: Optional[datetime.date] = None

@dataclass
class PtaPteHistory(Model):
    number: float
    date: datetime.date
    description: str
    pto_days: int
    applicant_days: int
    start: float

@dataclass
class PtaPteSummary(Model):
    a_delay: int
    b_delay: int
    c_delay: int
    overlap_delay: int
    pto_delay: int
    applicant_delay: int
    pto_adjustments: int
    total_days: int
    kind: Optional[str] = None

@dataclass
class Transaction(Model):
    date: datetime.date
    code: str
    description: str

@dataclass
class Correspondent(Model):
    name: str
    street: Optional[str] = None
    city: Optional[str] = None
    geo_region_code: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    cust_no: Optional[str] = None

@dataclass
class Attorney(Model):
    full_name: str
    phone_num: str
    reg_status: Optional[str] = None
    registration_no: Optional[int] = None

@dataclass
class Applicant(Model):
    name: Optional[str] = None
    cust_no: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    geo_region_code: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    rank_no: Optional[int] = None

@dataclass
class Expiration(Model):
    parent_appl_id: str
    parent_app_filing_date: datetime.date
    parent_relationship: str
    initial_term: datetime.date
    pta_or_pte: float
    extended_term: datetime.date
    terminal_disclaimer_filed: bool

@dataclass
class USApplication(Model):
    appl_id: str
    app_filing_date: Optional[datetime.date] = None
    app_location: Optional[str] = None
    patent_title: Optional[str] = None
    first_inventor_file: Optional[str] = None
    app_type: Optional[str] = None
    app_entity_status: Optional[str] = None
    app_confr_number: Optional[str] = None
    transactions: List[Transaction] = field(default_factory=list, repr=False)
    child_continuity: List[Relationship] = field(default_factory=list, repr=False)
    parent_continuity: List[Relationship] = field(default_factory=list, repr=False)
    pta_pte_tran_history: List[PtaPteHistory] = field(default_factory=list, repr=False)
    attorneys: List[Attorney] = field(default_factory=list, repr=False)
    applicants: List[Applicant] = field(default_factory=list, repr=False)
    app_status: Optional[str] = None
    app_status_date: Optional[datetime.date] = None
    app_cls_sub_cls: Optional[str] = None
    app_grp_art_number: Optional[str] = None
    correspondent: Optional[Correspondent] = field(default=None, repr=False)
    pta_pte_summary: Optional[PtaPteSummary] = field(default=None, repr=False)
    corr_addr_cust_no: Optional[str] = None
    app_cust_number: Optional[str] = None
    app_attr_dock_number: Optional[str] = None
    patent_number: Optional[str] = None
    patent_issue_date: Optional[datetime.date] = None
    app_early_pub_number: Optional[str] = None
    app_early_pub_date: Optional[datetime.date] = None
    app_exam_name: Optional[str] = None
    wipo_early_pub_number: Optional[str] = None
    wipo_early_pub_date: Optional[datetime.date] = None

    assignments = one_to_many('patent_client.uspto.assignment.Assignment', appl_id='appl_id')
    trials = one_to_many('patent_client.uspto.ptab.PtabProceeding', appl_id='appl_id')

    @property
    def expiration(self) -> Optional[Expiration]:
        if "PCT" in self.appl_id:
            raise NotImplementedError("Expiration date not supported for PCT Applications")
        if not self.patent_number:
            return None
        expiration_data = dict()
        term_parents = [
            p
            for p in self.parent_continuity
            if p.relationship
            not in ["Claims Priority from Provisional Application", "is a Reissue of"]
        ]
        if term_parents:
            term_parent = sorted(term_parents, key=lambda x: x.parent_app_filing_date)[
                0
            ]
            relationship = term_parent.relationship
            parent_filing_date = term_parent.parent_app_filing_date
            parent_appl_id = term_parent.parent_appl_id
        else:
            relationship = "self"
            parent_appl_id = self.appl_id
            parent_filing_date = self.app_filing_date

        expiration_data["parent_appl_id"] = parent_appl_id
        expiration_data["parent_app_filing_date"] = parent_filing_date
        expiration_data["parent_relationship"] = relationship
        expiration_data["initial_term"] = parent_filing_date + relativedelta(years=20) #type: ignore
        expiration_data["pta_or_pte"] = self.pta_pte_summary.total_days # type: ignore
        expiration_data["extended_term"] = expiration_data[
            "initial_term"
        ] + relativedelta(days=expiration_data["pta_or_pte"]) # type: ignore

        transactions = self.transactions
        try:
            disclaimer = next(t for t in transactions if t.code == "DIST")
            expiration_data["terminal_disclaimer_filed"] = True
        except StopIteration:
            expiration_data["terminal_disclaimer_filed"] = False

        return Expiration(**expiration_data) # type: ignore

