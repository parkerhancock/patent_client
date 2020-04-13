from __future__ import annotations

import datetime
from collections import OrderedDict
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional

from patent_client import session
from patent_client.util import Model
from patent_client.util import one_to_many
from patent_client.util import one_to_one
from patent_client.util import QuerySet


@dataclass
class Assignment(Model):
    __manager__ = "patent_client.uspto.assignment.manager.AssignmentManager"
    id: str
    conveyance_text: str
    last_update_date: str
    page_count: int
    recorded_date: datetime.date
    corr_name: str
    corr_address: str
    assignors: QuerySet[Assignor]
    assignees: QuerySet[Assignee]
    properties: QuerySet[Property] = field(repr=False)
    """Properties objects associated with this Assignment"""
    assignment_record_has_images: bool
    transaction_date: Optional[datetime.date] = None
    date_produced: Optional[datetime.date] = None

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
    invention_title: str
    inventors: str
    # Numbers
    appl_id: str
    pct_num: str
    intl_reg_num: str
    publ_num: str
    pat_num: str
    # Dates
    filing_date: datetime.date
    intl_publ_date: datetime.date
    issue_date: datetime.date
    publ_date: datetime.date

    us_application = one_to_one("patent_client.USApplication", appl_id="appl_id")
    """A USApplication object related to the property"""


@dataclass
class Person(Model):
    name: str
    address: str
    city: str
    state: str
    post_code: str
    country_name: str


@dataclass
class Assignor(Model):
    name: str
    ex_date: datetime.date
    date_ack: datetime.datetime


@dataclass
class Assignee(Model):
    name: str
    address: str
    city: str
    state: str
    country_name: str
    postcode: str
