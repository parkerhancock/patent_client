import datetime
from typing import List
from typing import Optional
from typing import TypeVar

from patent_client.util.pydantic_util import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated


class PublicSearchBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        anystr_strip_whitespace=True,
    )


T = TypeVar("T")


OptionalList = Annotated[List[T], BeforeValidator(lambda x: x if isinstance(x, list) else list())]
DateTimeAsDate = Annotated[
    datetime.date, BeforeValidator(lambda x: x.date() if isinstance(x, datetime.datetime) else x)
]


def format_appl_id(string):
    if string.startswith("D"):
        string = "29" + string[1:]
    return string.replace("/", "")


ApplicationNumber = Annotated[str, BeforeValidator(format_appl_id)]


class DocumentStructure(BaseModel):
    number_of_claims: Optional[int] = None
    number_of_drawing_sheets: Optional[int] = None
    number_of_figures: Optional[int] = None
    page_count: Optional[int] = None
    front_page_end: Optional[int] = None
    front_page_start: Optional[int] = None
    bib_start: Optional[int] = None
    bib_end: Optional[int] = None
    abstract_start: Optional[int] = None
    abstract_end: Optional[int] = None
    drawings_start: Optional[int] = None
    drawings_end: Optional[int] = None
    description_start: Optional[int] = None
    description_end: Optional[int] = None
    specification_start: Optional[int] = None
    specification_end: Optional[int] = None
    claims_end: Optional[int] = None
    claims_start: Optional[int] = None
    amend_start: Optional[int] = None
    amend_end: Optional[int] = None
    cert_correction_end: Optional[int] = None
    cert_correction_start: Optional[int] = None
    cert_reexamination_end: Optional[int] = None
    cert_reexamination_start: Optional[int] = None
    ptab_start: Optional[int] = None
    ptab_end: Optional[int] = None
    search_report_start: Optional[int] = None
    search_report_end: Optional[int] = None
    supplemental_start: Optional[int] = None
    supplemental_end: Optional[int] = None
