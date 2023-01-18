from __future__ import annotations

import datetime
from dataclasses import dataclass
from dataclasses import field
from typing import *

from patent_client import session
from patent_client.util import Model
from patent_client.util.base.related import get_model
from yankee.data import ListCollection


@dataclass
class AssignmentPage:
    num_found: int
    docs: "List[Assignment]" = field(default_factory=ListCollection)


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
    assignors: "ListCollection[Assignor]" = field(default_factory=ListCollection)
    assignees: "ListCollection[Assignee]" = field(default_factory=ListCollection)
    properties: "ListCollection[Property]" = field(repr=False, default_factory=ListCollection)
    """Properties objects associated with this Assignment"""
    assignment_record_has_images: bool = False
    transaction_date: "Optional[datetime.date]" = None
    date_produced: "Optional[datetime.date]" = None

    @property
    def image_url(self) -> str:
        reel, frame = self.id.split("-")
        reel = reel.rjust(6, "0")
        frame = frame.rjust(4, "0")
        return f"http://legacy-assignments.uspto.gov/assignments/assignment-pat-{reel}-{frame}.pdf"

    def download(self):
        """downloads the PDF associated with the assignment to the current working directory"""
        response = session.get(self.image_url, stream=True)
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

    def __repr__(self):
        return f"Property(appl_id={self.appl_id}, invention_title={self.invention_title})"

    @property
    def application(self) -> "patent_client.uspto.peds.model.USApplication":
        """The related US Application"""
        return get_model("patent_client.uspto.peds.model.USApplication").objects.get(appl_id=self.appl_id)

    @property
    def patent(self) -> "patent_client.uspto.fulltext.patent.model.Patent":
        """The related US Patent, if any"""
        return get_model("patent_client.uspto.peds.fulltext.patent.model.Patent").objects.get(
            publication_number=self.pat_num
        )

    @property
    def publication(self) -> "patent_client.uspto.fulltext.published_application.model.PublishedApplication":
        """The related US Publication, if any"""
        return get_model("patent_client.uspto.peds.fulltext.patent.model.PublishedApplication").objects.get(
            publication_number=self.publ_num
        )


@dataclass
class Assignor(Model):
    name: str
    ex_date: datetime.date
    date_ack: datetime.datetime = None


@dataclass
class Assignee(Model):
    name: str
    address: "Optional[str]" = None
