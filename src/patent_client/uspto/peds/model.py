from __future__ import annotations

import datetime
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Iterable
from typing import List
from typing import Optional

from dateutil.relativedelta import relativedelta
from patent_client import session
from patent_client.util import Model
from patent_client.util.base.related import get_model
from yankee.data import ListCollection


@dataclass
class USApplication(Model):
    """A U.S. Patent Application retrieved from the Patent Examination Data
    System (PEDS)
    """

    __manager__ = "patent_client.uspto.peds.manager.USApplicationManager"

    appl_id: str = field(compare=True)
    """The application number. U.S. Applications are digits only.
    PCT numbers are in the format PCT/CCYY/#####"""

    app_filing_date: Optional[datetime.date] = field(default=None, repr=False)
    """The filing date or 371(c) date"""

    patent_title: "Optional[str]" = None
    """Title of the invention"""

    app_status: "Optional[str]" = field(default=None, repr=True)
    """Status of the Application"""

    app_status_date: Optional[datetime.date] = field(default=None, repr=False)
    """The date of the applicable status (the app_status attribute)"""

    app_early_pub_number: "Optional[str]" = field(default=None, repr=False)
    """The published patent application number in the format USYYYY#######A1
    Note: this does not include subsequent or corrected publications, or publications
    of PCT applications."""

    app_early_pub_date: Optional[datetime.date] = field(default=None, repr=False)
    """The publication date of the publication mentioned in app_early_pub_number"""

    patent_number: "Optional[str]" = field(default=None, repr=False)
    """The issued patent number, if any. Digits only"""

    patent_issue_date: Optional[datetime.date] = field(default=None, repr=False)
    """The date the patent issued"""

    wipo_early_pub_number: "Optional[str]" = field(default=None, repr=False)
    """If the application was published by WIPO (i.e. a PCT application),
    the publication number is here. Format is YYYY######"""

    wipo_early_pub_date: Optional[datetime.date] = field(default=None, repr=False)
    """Publication date by WIPO"""

    corr_addr_cust_no: "Optional[str]" = field(default=None, repr=False)
    """The customer number for the correspondent named for this application"""

    app_cust_number: "Optional[str]" = field(default=None, repr=False)
    """The customer number for the firm with authority to act in the application"""

    app_attr_dock_number: "Optional[str]" = field(default=None, repr=False)
    """The docket number assigned to the application by the handling firm"""

    app_location: "Optional[str]" = field(default=None, repr=False)
    """The physical location of the application file"""

    first_inventor_file: "Optional[str]" = field(default=None, repr=False)
    """Whether the application is examined under the America Invents Act"""

    app_type: "Optional[str]" = field(default=None, repr=False)
    """The subject matter of the application (i.e. Utility / Design / Plant)"""

    app_entity_status: "Optional[str]" = field(default=None, repr=False)
    """The entity type of the owner (UNDISCOUNTED / SMALL / MICRO)"""

    app_confr_number: "Optional[str]" = field(default=None, repr=False)
    """The application's confirmation number"""

    app_cls_sub_cls: "Optional[str]" = field(default=None, repr=False)
    """The U.S. classification assigned to the application"""

    app_grp_art_number: "Optional[str]" = field(default=None, repr=False)
    """The Group Art Unit to which the application is assigned"""

    app_exam_name: "Optional[str]" = field(default=None, repr=False)
    """The name of the examiner handling the application"""

    # Nested Objects
    pta_pte_summary: Optional[PtaPteSummary] = field(default=None, repr=False)
    """A related object containing the PTA/PTE analysis"""

    correspondent: Optional[Correspondent] = field(default=None, repr=False)
    """Correspondent for the Application"""

    # List Properties
    inventors: ListCollection[Inventor] = field(default=None, repr=False)
    """List of named inventors"""

    applicants: ListCollection[Applicant] = field(default_factory=list, repr=False)
    """List of named applicants"""

    attorneys: ListCollection[Attorney] = field(default_factory=list, repr=False)
    """List of attorneys authorized to act in this application, associated with
    the indicated customer number"""

    transactions: ListCollection[Transaction] = field(default_factory=list, repr=False)
    """List of transactions relating to this application. Identical to the "Transactions" tab on
    Patent Center or Private PAIR"""

    child_continuity: ListCollection[Relationship] = field(default_factory=ListCollection, repr=False)
    """List of related Applications which claim priority to this application. Note that
    this does not include continuity type (e.g. CON/CIP/DIV)"""

    parent_continuity: ListCollection[Relationship] = field(default_factory=ListCollection, repr=False)
    """List of related Applications that this application claims priority to, including
    continuity type. Does not include foreign priority claims"""

    foreign_priority: ListCollection[ForeignPriority] = field(default_factory=list, repr=False)
    """List of foreign patent applications to which this application claims priority"""

    pta_pte_tran_history: ListCollection[PtaPteHistory] = field(default_factory=list, repr=False)
    """List of transactions relevant to calculating a Patent Term Extension or Adjustment"""

    assignments: ListCollection[Assignment] = field(default_factory=ListCollection, repr=False)
    """List of Assignments that include this application"""

    def __hash__(self):
        return hash(self.appl_id)

    # Dynamic Properties

    @property
    def patent_center_link(self) -> str:
        return f"https://patentcenter.uspto.gov/applications/{self.appl_id}"

    @property
    def google_patents_link(self) -> str:
        if self.patent_number is not None:
            return f"https://patents.google.com/patent/US{self.patent_number}/en"
        elif self.app_early_pub_number is not None:
            return f"https://patents.google.com/patent/{self.app_early_pub_number}/en"
        else:
            return None

    @property
    def continuity(self) -> ListCollection[USApplication]:
        """Returns a complete set of parents, self, and children"""
        return ListCollection(
            [
                self.child_continuity.values_list("child", flat=True),
                [
                    self,
                ],
                self.parent_continuity.values_list("parent", flat=True),
            ]
        )

    @property
    def kind(self) -> str:
        """Differentiates provisional, PCT, and nonprovisional applications"""
        if "PCT" in self.appl_id:
            return "PCT"
        if self.appl_id[0] == "6":
            return "Provisional"
        return "Nonprovisional"

    @property
    def publication_number(self):
        return self.app_early_pub_number[2:-2]

    @property
    def priority_date(self) -> datetime.date:
        """Attempts to return the priority date of the application, calculated as
        the earliest application filing date among the application's parents, or
        its own filing date if it has no parents. Does not include foreign priority
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
            raise NotImplementedError("Expiration date not supported for PCT Applications")
        if not self.patent_number:
            return None
        expiration_data = dict()
        term_parents = [
            p
            for p in self.parent_continuity
            if p.relationship not in ["Claims Priority from Provisional Application", "is a Reissue of"]
        ]
        if term_parents:
            term_parent = sorted(term_parents, key=lambda x: x.parent_app_filing_date)[0]
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
        expiration_data["pta_or_pte"] = self.pta_pte_summary.total_days or 0  # type: ignore
        expiration_data["extended_term"] = expiration_data["initial_term"] + relativedelta(
            days=expiration_data["pta_or_pte"]
        )  # type: ignore

        transactions = self.transactions
        try:
            disclaimer = next(t for t in transactions if t.code == "DIST")
            expiration_data["terminal_disclaimer_filed"] = True
        except StopIteration:
            expiration_data["terminal_disclaimer_filed"] = False

        return Expiration(**expiration_data)  # type: ignore

    # Related objects
    @property
    def documents(self) -> "Iterable[patent_client.uspto.peds.model.Document]":
        """File History Documents from PEDS CMS"""
        return get_model("patent_client.uspto.peds.model.Document").objects.filter(appl_id=self.appl_id)

    @property
    def related_assignments(self) -> "Iterable[patent_client.uspto.assignment.model.Assignment]":
        """Related Assignments from the Assignments API"""
        return get_model("patent_client.uspto.assignment.model.Assignment").objects.filter(appl_id=self.appl_id)

    @property
    def ptab_proceedings(self) -> "Iterable[patent_client.uspto.ptab.model.PtabProceeding]":
        """Related PtabProceedings for this application"""
        return get_model("patent_client.uspto.ptab.model.PtabProceeding").objects.filter(appl_id=self.appl_id)

    @property
    def patent(self) -> "Optional[patent_client.uspto.fulltext.patent.model.Patent]":
        """Fulltext version of the patent - If Available"""
        return get_model("patent_client.uspto.fulltext.patent.model.Patent").objects.get(
            publication_number=self.patent_number
        )

    @property
    def publication(self) -> "Optional[patent_client.uspto.fulltext.published_application.model.PublishedApplication]":
        """Fulltext version of the Publication - If Available"""
        return get_model(
            "patent_client.uspto.fulltext.published_application.model.PublishedApplication",
            publication_number=self.publication_number,
        )

    @property
    def inpadoc_patent(self) -> "Optional[patent_client.epo.ops.published.model.InpadocBiblio]":
        """Fulltext version of the patent - If Available"""
        return get_model(
            "patent_client.epo.ops.published.model.InpadocBiblio", publication_number=f"US{self.patent_number}"
        )

    @property
    def inpadoc_publication(self) -> "Optional[patent_client.epo.ops.published.model.InpadocBiblio]":
        """Fulltext version of the patent - If Available"""
        return get_model(
            "patent_client.epo.ops.published.model.InpadocBiblio", publication_number=self.app_early_pub_number
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


@dataclass
class Relationship(Model):
    parent_appl_id: str
    """The application number of the parent application"""
    child_appl_id: str
    """The application number of the child application"""
    relationship: "Optional[str]"
    """The relationship of the parent to child. This information
    is only populated on Relationships associated with the child application"""
    child_app_filing_date: "Optional[datetime.date]" = None
    """The filing date of the child application"""
    parent_app_filing_date: "Optional[datetime.date]" = None
    """The filing date of the parent application"""
    parent_app_status: "Optional[str]" = None
    """The status of the parent application - which may not be indicated"""
    child_app_status: "Optional[str]" = None
    """The status of the chidl application - which may not be indicated"""

    @property
    def parent(self) -> "patent_client.uspto.peds.USApplication":
        """Link to the parent application"""
        return get_model("patent_client.uspto.peds.USApplication").objects.get(appl_id=self.parent_appl_id)

    @property
    def child(self) -> "patent_client.uspto.peds.USApplication":
        """Link to the child application"""
        return get_model("patent_client.uspto.peds.USApplication").objects.get(appl_id=self.child_appl_id)

    def __eq__(self, other):
        return (
            self.parent_appl_id == other.parent_appl_id
            and self.child_appl_id == other.child_appl_id
            and self.relationship == other.relationship
        )

    def __hash__(self):
        return hash((self.parent_appl_id, self.child_appl_id, self.relationship))


@dataclass
class ForeignPriority(Model):
    priority_claim: str
    """The application number of the foreign priority application"""
    country_name: str
    """The country in which the foreign priorty application was filed"""
    filing_date: datetime.date
    """The filing date of the foreign priority application"""


@dataclass
class PtaPteHistory(Model):
    number: float
    date: datetime.date
    description: str
    pto_days: "Optional[float]" = None
    applicant_days: "Optional[float]" = None
    start: "Optional[float]" = None


@dataclass
class PtaPteSummary(Model):
    a_delay: "Optional[int]" = None
    b_delay: "Optional[int]" = None
    c_delay: "Optional[int]" = None
    overlap_delay: "Optional[int]" = None
    pto_delay: "Optional[int]" = None
    applicant_delay: "Optional[int]" = None
    pto_adjustments: "Optional[int]" = None
    total_days: "Optional[int]" = None
    kind: "Optional[str]" = None


@dataclass
class Transaction(Model):
    date: datetime.date
    code: str
    description: str


@dataclass
class Correspondent(Model):
    name: str
    address: "Optional[str]" = None
    cust_no: "Optional[str]" = None


@dataclass
class Attorney(Model):
    name: str
    phone_num: str
    reg_status: "Optional[str]" = None
    registration_no: Optional[int] = None


@dataclass
class Applicant(Model):
    name: "Optional[str]" = None
    cust_no: "Optional[str]" = None
    address: "Optional[str]" = None
    rank_no: Optional[int] = None


@dataclass
class Inventor(Model):
    name: "Optional[str]" = None
    address: "Optional[str]" = None
    rank_no: Optional[int] = None


class PedsError(Exception):
    pass


@dataclass
class Document(Model):
    __manager__ = "patent_client.uspto.peds.manager.DocumentManager"
    base_url = "https://ped.uspto.gov/api/queries/cms/public/"
    access_level_category: str
    appl_id: str
    category: str
    code: str
    description: str
    identifier: str
    mail_room_date: datetime.date
    page_count: int
    url: "Optional[str]" = None

    @property
    def application(self) -> "patent_client.uspto.peds.model.USApplication":
        return get_model("patent_client.uspto.peds.model.USApplication").objects.get(appl_id=self.appl_id)

    def __repr__(self):
        return f"Document(appl_id={self.appl_id}, mail_room_date={self.mail_room_date}, description={self.description})"

    def download(self, path=".", include_appl_id=True):
        if str(path)[-4:].lower() == ".pdf":
            # If we've been given a specific filename, use it
            out_file = Path(path)
        elif include_appl_id:
            out_file = (
                Path(path) / f"{self.appl_id} - {self.mail_room_date} - {self.code} - {self.description[:40]}.pdf"
            )
        else:
            out_file = Path(path) / f"{self.mail_room_date} - {self.code} - {self.description[:40]}.pdf"

        with session.get(self.base_url + self.url, stream=True) as r:
            if r.status_code == 403:
                raise PedsError("File history document downloading is broken. This is a USPTO problem :(")
            r.raise_for_status()
            with out_file.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return out_file


@dataclass
class Assignee(Model):
    name: str = None
    address: str = None


@dataclass
class Assignor(Model):
    name: str = None
    exec_date: "datetime.date" = None


@dataclass
class Assignment(Model):
    id: str
    correspondent: str = None
    correspondent_address: str = None
    mail_date: "datetime.date" = None
    received_date: "datetime.date" = None
    recorded_date: "datetime.date" = None
    pages: int = None
    conveyance_text: str = None
    sequence_number: int = None
    assignors: "ListCollection[Assignor]" = field(default_factory=ListCollection)
    assignees: "ListCollection[Assignee]" = field(default_factory=ListCollection)


@dataclass
class PedsPage(Model):
    index_last_updated: datetime.date
    num_found: int
    applications: "List[USApplication]" = field(default_factory=list)
