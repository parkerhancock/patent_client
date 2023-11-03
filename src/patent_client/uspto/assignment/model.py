from __future__ import annotations

import datetime
import warnings
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import *

from patent_client.util import Model
from patent_client.util.asyncio_util import run_sync
from patent_client.util.base.related import get_model
from yankee.data import ListCollection

from .api import AssignmentApi

if TYPE_CHECKING:
    from patent_client.uspto.peds.model import USApplication
    from patent_client.uspto.public_search.model import Patent, PublishedApplication


@dataclass
class AssignmentPage:
    num_found: int
    docs: "List[Assignment]" = field(default_factory=ListCollection)


@dataclass
class Assignment(Model):
    id: str
    conveyance_text: str
    last_update_date: str
    page_count: int
    recorded_date: datetime.date
    corr_name: Optional[str] = None
    corr_address: Optional[str] = None
    assignors: "ListCollection[Assignor]" = field(default_factory=ListCollection)
    assignees: "ListCollection[Assignee]" = field(default_factory=ListCollection)
    properties: "ListCollection[Property]" = field(repr=False, default_factory=ListCollection)
    """Properties objects associated with this Assignment"""
    assignment_record_has_images: bool = False
    transaction_date: Optional[datetime.date] = None
    date_produced: Optional[datetime.date] = None

    @property
    def reel_frame(self):
        return self.id.split("-")

    @property
    def image_url(self):
        return AssignmentApi.get_download_url(*self.reel_frame)

    def download(self, path: Optional[str | Path] = None):
        """downloads the PDF associated with the assignment to the current working directory"""
        return run_sync(self.adownload(path=path))

    async def adownload(self, path: Optional[str | Path] = None):
        """asynchronously downloads the PDF associated with the assignment to the current working directory"""
        return await AssignmentApi.download_pdf(*self.reel_frame, path=path)


@dataclass
class Property(Model):
    appl_id: Optional[str] = None
    invention_title: Optional[str] = None
    inventors: Optional[str] = None
    # Numbers
    pct_num: Optional[str] = None
    intl_reg_num: Optional[str] = None
    publ_num: Optional[str] = None
    pat_num: Optional[str] = None
    # Dates
    filing_date: Optional[datetime.date] = None
    intl_publ_date: Optional[datetime.date] = None
    issue_date: Optional[datetime.date] = None
    publ_date: Optional[datetime.date] = None

    def __repr__(self):
        return f"Property(appl_id={self.appl_id}, invention_title={self.invention_title})"

    @property
    def application(self) -> Optional["USApplication"]:
        """The related US Application"""
        try:
            appl_id = getattr(self, "appl_id", None)
            if appl_id is not None:
                return get_model("patent_client.uspto.peds.model.USApplication").objects.get(appl_id=appl_id)
            appl_id = getattr(self, "pct_num", None)
            if appl_id is not None:
                return get_model("patent_client.uspto.peds.model.USApplication").objects.get(appl_id=appl_id)
            pub_num = getattr(self, "publ_num", None)
            if pub_num is not None:
                return get_model("patent_client.uspto.peds.model.USApplication").objects.get(
                    app_early_pub_number=pub_num
                )
            pat_num = getattr(self, "pat_num", None)
            if pat_num is not None:
                return get_model("patent_client.uspto.peds.model.USApplication").objects.get(patent_number=pat_num)
        except Exception:
            pass
        warnings.warn(f"Unable to find application for {self}")
        return None

    @property
    def patent(self) -> "Patent":
        """The related US Patent, if any"""
        return get_model("patent_client.uspto.public_search.model.Patent").objects.get(publication_number=self.pat_num)

    @property
    def publication(
        self,
    ) -> "PublishedApplication":
        """The related US Publication, if any"""
        return get_model("patent_client.uspto.peds.fulltext.patent.model.PublishedApplication").objects.get(
            publication_number=self.publ_num
        )


@dataclass
class Assignor(Model):
    name: str
    ex_date: datetime.date
    date_ack: Optional[datetime.datetime] = None


@dataclass
class Assignee(Model):
    name: str
    address: Optional[str] = None
