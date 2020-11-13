from __future__ import annotations

import datetime
from collections import OrderedDict
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import Dict
from typing import List
from typing import Optional

from dateutil.relativedelta import relativedelta
from patent_client.util import ListManager
from patent_client.util import Model
from patent_client.util import one_to_many
from patent_client.util import one_to_one
from patent_client.util import QuerySet


@dataclass
class USApplication(Model):
    __manager__ = "patent_client.uspto.peds.manager.USApplicationManager"
    appl_id: str = field(compare=True)
    patent_title: Optional[str] = None
    app_status: Optional[str] = field(default=None, repr=True)
    inventors: Optional[List[str]] = field(default=None, repr=False)
    app_filing_date: Optional[datetime.date] = field(default=None, repr=False)
    app_location: Optional[str] = field(default=None, repr=False)
    first_inventor_file: Optional[str] = field(default=None, repr=False)
    app_type: Optional[str] = field(default=None, repr=False)
    app_entity_status: Optional[str] = field(default=None, repr=False)
    app_confr_number: Optional[str] = field(default=None, repr=False)
    applicants: List[Applicant] = field(default_factory=list, repr=False)
    app_status_date: Optional[datetime.date] = field(default=None, repr=False)
    app_cls_sub_cls: Optional[str] = field(default=None, repr=False)
    app_grp_art_number: Optional[str] = field(default=None, repr=False)
    corr_addr_cust_no: Optional[str] = field(default=None, repr=False)
    app_cust_number: Optional[str] = field(default=None, repr=False)
    app_attr_dock_number: Optional[str] = field(default=None, repr=False)
    patent_number: Optional[str] = field(default=None, repr=False)
    patent_issue_date: Optional[datetime.date] = field(default=None, repr=False)
    app_early_pub_number: Optional[str] = field(default=None, repr=False)
    app_early_pub_date: Optional[datetime.date] = field(default=None, repr=False)
    app_exam_name: Optional[str] = field(default=None, repr=False)
    wipo_early_pub_number: Optional[str] = field(default=None, repr=False)
    wipo_early_pub_date: Optional[datetime.date] = field(default=None, repr=False)

    transactions: List[Transaction] = field(default_factory=list, repr=False)
    child_continuity: ListManager[Relationship] = field(
        default_factory=ListManager.empty, repr=False
    )
    parent_continuity: ListManager[Relationship] = field(
        default_factory=ListManager.empty, repr=False
    )
    pta_pte_tran_history: List[PtaPteHistory] = field(default_factory=list, repr=False)
    pta_pte_summary: Optional[PtaPteSummary] = field(default=None, repr=False)
    correspondent: Optional[Correspondent] = field(default=None, repr=False)
    attorneys: List[Attorney] = field(default_factory=list, repr=False)
    foreign_priority: List[ForeignPriority] = field(default_factory=list, repr=False)

    @property
    def continuity(self) -> QuerySet:
        """Returns a complete set of parents, self, and children"""
        return QuerySet(
            [
                self.child_continuity.values_list("child", flat=True),
                [self,],
                self.parent_continuity.values_list("parent", flat=True),
            ]
        )

    def __hash__(self):
        return hash(self.appl_id)

    @property
    def kind(self) -> str:
        """Differentiates provisional, PCT, and nonprovisional applications"""
        if "PCT" in self.appl_id:
            return "PCT"
        if self.appl_id[0] == "6":
            return "Provisional"
        return "Nonprovisional"

    @property
    def priority_date(self) -> datetime.date:
        """Attempts to return the priority date of the application, calculated as
        the earliest application filing date among the application's parents, or
        its own filing date if it has no parents
        """
        if not self.parent_continuity:
            return self.app_filing_date
        else:
            return sorted(p.parent_app_filing_date for p in self.parent_continuity)[0]

    @property
    def expiration(self) -> Optional[Expiration]:
        """Calculates expiration data from which the expiration date can be calculated. See
        help information for the resulting Expiration model.
        """
        if "PCT" in self.appl_id:
            raise NotImplementedError(
                "Expiration date not supported for PCT Applications"
            )
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
        expiration_data["initial_term"] = parent_filing_date + relativedelta(years=20)  # type: ignore
        expiration_data["pta_or_pte"] = self.pta_pte_summary.total_days if self.pta_pte_summary else 0  # type: ignore
        expiration_data["extended_term"] = expiration_data[
            "initial_term"
        ] + relativedelta(
            days=expiration_data["pta_or_pte"]
        )  # type: ignore

        transactions = self.transactions
        try:
            disclaimer = next(t for t in transactions if t.code == "DIST")
            expiration_data["terminal_disclaimer_filed"] = True
        except StopIteration:
            expiration_data["terminal_disclaimer_filed"] = False

        return Expiration(**expiration_data)  # type: ignore

    assignments = one_to_many(
        "patent_client.uspto.assignment.Assignment", appl_id="appl_id"
    )
    """Related Assignments from the Assignments API"""
    trials = one_to_many(
        "patent_client.uspto.ptab.PtabProceeding", appl_id="appl_id"
    )
    """Related PtabProceedings for this application"""
    patent = one_to_one(
        "patent_client.uspto.fulltext.Patent", publication_number="patent_number"
    )
    """Fulltext Patent - If Available"""

    @property
    def publication_number(self):
        return self.app_early_pub_number[2:-2]

    publication = one_to_one(
        "patent_client.uspto.fulltext.PublishedApplication", publication_number="publication_number"
    )


@dataclass
class Expiration(Model):
    """Model for patent application expiration data.
    NOTE: THIS IS NOT LEGAL ADVICE. See MPEP Sec. 2701 for a detailed explanation of calculating patent term

    This model provides a first-cut estimate of patent term by calulating four things:

    1. The earliest-filed non-provisional patent application (EFNP) from which term should be calculated (parent).
    2. 20 years from the filing date of the EFNP (initial term)
    3. Extensions from Patent Term Extentions (PTE) or Patent Term Adjustments (PTA) (extended_term)
    4. The presence or absence of a terminal disclaimer in the transaction history

    """

    parent_appl_id: str
    """Application number for the earliest-filed nonprovisional application related to this application, or self"""
    parent_app_filing_date: datetime.date
    """Filing date of the earliest-filed nonprovisional application related to this application, or self"""
    parent_relationship: str
    """Relationship of the earliest-filed nonprovisional application. Can be self"""
    initial_term: datetime.date
    """Patent term calculated as 20 years from earliest-field non-provisional (no adjustments)"""
    pta_or_pte: float
    """Days of extended patent term from a Patent Term Extension (PTE) or Patent Term Adjustment (PTA)"""
    extended_term: datetime.date
    """Patent term as extended by any applicable Patent Term Extension or Patent Term Adjustment"""
    terminal_disclaimer_filed: bool
    """Presence or absence of a terminal disclaimer in the transaction history of the application"""


@dataclass(frozen=True)
class Relationship(Model):
    parent_appl_id: str
    child_appl_id: str
    relationship: str
    child_app_filing_date: Optional[datetime.date] = None
    parent_app_filing_date: Optional[datetime.date] = None
    parent = one_to_one(
        "patent_client.uspto.peds.USApplication", appl_id="parent_appl_id"
    )
    child = one_to_one(
        "patent_client.uspto.peds.USApplication", appl_id="child_appl_id"
    )


@dataclass
class ForeignPriority(Model):
    priority_claim: str
    country_name: str
    filing_date: datetime.date


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
class Inventor(Model):
    name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    geo_code: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    rank_no: Optional[int] = None
