import datetime
import warnings
from pathlib import Path
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from dateutil.parser import isoparse
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from patent_client.util.asyncio_util import run_sync
from patent_client.util.pydantic_util import BaseModel
from patent_client.util.related import get_model

if TYPE_CHECKING:
    from patent_client.uspto.peds.model import USApplication
    from patent_client.uspto.public_search.model import Patent, PublishedApplication
    from .manager import AssignmentManager

from .session import session

UsptoDate = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.strptime(x, "%Y%m%d").date())]
YNBool = Annotated[bool, BeforeValidator(lambda x: x == "Y")]


def parse_datetime(string):
    dt = isoparse(string)
    if dt.year == 1 and dt.month == 1 and dt.day == 1:
        return None
    return dt


def parse_date(string):
    dt = parse_datetime(string)
    if dt is None:
        return None
    return dt.date()


DatetimeAsDate = Annotated[Optional[datetime.date], BeforeValidator(lambda x: parse_date(x))]


class AbstractAssignmentModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        str_strip_whitespace=True,
    )


class Assignor(AbstractAssignmentModel):
    name: str = Field(alias="patAssignorName")
    execution_date: DatetimeAsDate = Field(alias="patAssignorExDate")
    acknowledgement_date: DatetimeAsDate = Field(alias="patAssignorDateAck")


class Assignee(AbstractAssignmentModel):
    name: str = Field(alias="patAssigneeName")
    address: str = Field(alias="patAssigneeAddress")


class Property(AbstractAssignmentModel):
    invention_title: str
    invention_title_lang: str
    appl_num: str
    filing_date: Optional[DatetimeAsDate] = None
    intl_publ_date: Optional[DatetimeAsDate] = None
    intl_reg_num: Optional[str] = None
    inventors: Optional[str] = None
    issue_date: Optional[DatetimeAsDate] = None
    pat_num: Optional[str] = None
    pct_num: Optional[str] = None
    publ_date: Optional[DatetimeAsDate] = None
    publ_num: Optional[str] = None

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


class Correspondent(AbstractAssignmentModel):
    name: str
    address: str


class Assignment(AbstractAssignmentModel["AssignmentManager"]):
    id: str
    date_produced: Optional[UsptoDate] = None
    action_key_code: Optional[str] = None
    transaction_date: Optional[DatetimeAsDate] = None
    last_update_date: DatetimeAsDate
    purge_indicator: YNBool
    recorded_date: DatetimeAsDate
    page_count: int
    conveyance_text: str
    assignment_record_has_images: YNBool
    attorney_dock_num: Optional[str] = None
    pat_assignor_earliest_ex_date: DatetimeAsDate
    correspondent: Correspondent
    assignors: List[Assignor]
    assignees: List[Assignee]
    properties: List[Property]

    @field_validator("conveyance_text")
    @classmethod
    def remove_see_document(cls, v) -> str:
        return v.replace(" (SEE DOCUMENT FOR DETAILS).", "").strip()

    @property
    def reel_frame(self):
        return self.id.split("-")

    @property
    def image_url(self):
        reel, frame = self.reel_frame
        reel = reel.rjust(6, "0")
        frame = frame.rjust(4, "0")
        return f"http://legacy-assignments.uspto.gov/assignments/assignment-pat-{reel}-{frame}.pdf"

    def download(self, path: Optional[str | Path] = None):
        """downloads the PDF associated with the assignment to the current working directory"""
        return run_sync(self.adownload(path=path))

    async def adownload(self, path: Optional[str | Path] = None):
        """asynchronously downloads the PDF associated with the assignment to the current working directory"""
        return await session.download(self.image_url, path=path)


class AssignmentPage(AbstractAssignmentModel):
    num_found: int
    docs: list[Assignment]
