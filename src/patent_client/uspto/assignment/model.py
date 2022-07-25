from __future__ import annotations

import datetime
from dataclasses import dataclass
from dataclasses import field

from patent_client import session
from patent_client.util import Model
from patent_client.util import QuerySet
from patent_client.util import one_to_many
from patent_client.util import one_to_one

@dataclass
class AssignmentPage():
    num_found: int
    docs: "List[Assignment]" = field(default_factory=list)

@dataclass
class Assignment(Model):
    __manager__ = "patent_client.uspto.assignment.manager.AssignmentManager"
    id: str
    conveyance_text: str
    last_update_date: str
    page_count: int
    recorded_date: datetime.date
    corr_name: str = None
    corr_address: str = None
    assignors: "QuerySet[Assignor]" = field(default_factory=list)
    assignees: "QuerySet[Assignee]" = field(default_factory=list)
    properties: "QuerySet[Property]" = field(repr=False, default_factory=list)
    """Properties objects associated with this Assignment"""
    assignment_record_has_images: bool = False
    transaction_date: "Optional[datetime.date]" = None
    date_produced: "Optional[datetime.date]" = None

    @property
    def _image_url(self):
        reel, frame = self.id.split("-")
        reel = reel.rjust(6, "0")
        frame = frame.rjust(4, "0")
        return f"http://legacy-assignments.uspto.gov/assignments/assignment-pat-{reel}-{frame}.pdf"

    def download(self):
        """downloads the PDF associated with the assignment to the current working directory"""
        response = session.get(self._image_url, stream=True)
        with open(f"{self.id}.pdf", "wb") as f:
            f.write(response.raw.read())


@dataclass
class Property(Model):
    appl_id: str
    invention_title: "Optional[str]" = None
    inventors: "Optional[str]" = None
    # Numbers
    pct_num: "Optional[str]" = None
    intl_reg_num: "Optional[str]" = None
    publ_num: "Optional[str]" = None
    pat_num: "Optional[str]" = None
    # Dates
    filing_date: "Optional[datetime.date]" = None
    intl_publ_date: "Optional[datetime.date]" = None
    issue_date: "Optional[datetime.date]" = None
    publ_date: "Optional[datetime.date]" = None

    us_application = one_to_one("patent_client.USApplication", appl_id="appl_id")
    """A USApplication object related to the property"""

@dataclass
class Assignor(Model):
    name: str
    ex_date: datetime.date
    date_ack: datetime.datetime = None


@dataclass
class Assignee(Model):
    name: str
    address: "Optional[str]" = None
