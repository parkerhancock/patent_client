import datetime
from pathlib import Path
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta
from patent_client.util.asyncio_util import run_sync
from patent_client.util.pydantic_util import BaseModel
from patent_client.util.related import get_model
from pydantic import AliasPath
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated
from typing_extensions import Self

from .session import session

if TYPE_CHECKING:
    from patent_client import PtabProceeding, Patent, PublishedApplication
    from patent_client.epo.ops.published.model import InpadocBiblio


DateTimeAsDate = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.fromisoformat(x).date())]
MDYDate = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.strptime(x, "%m-%d-%Y").date())]
YNBool = Annotated[bool, BeforeValidator(lambda x: x == "Y")]
OptionalInt = Annotated[Optional[int], BeforeValidator(lambda x: int(x) if x else None)]
RelationshipStr = Annotated[str, BeforeValidator(lambda x: x.replace("This application ", "").strip())]


class PEDSBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        str_strip_whitespace=True,
    )


class Transactions(PEDSBaseModel):
    record_date: DateTimeAsDate
    code: str
    description: str


class PtaOrPteTransactionHistory(PEDSBaseModel):
    number: float
    pta_or_pte_date: MDYDate
    contents_description: str
    pto_days: OptionalInt
    appl_days: OptionalInt
    start: float


class PtaOrPteSummary(PEDSBaseModel):
    a_delay: int
    b_delay: int
    c_delay: int
    pto_adjustments: int
    total_days: int = Field(alias="totalPtoDays")
    kind: str = Field(alias="ptaPteInd")
    pto_delay: int
    applicant_delay: int = Field(alias="applDelay")
    overlap_delay: int


class ParentApplication(PEDSBaseModel):
    parent_appl_id: str = Field(alias="claimApplicationNumberText")
    child_appl_id: str = Field(alias="applicationNumberText")
    parent_app_filing_date: MDYDate = Field(alias="filingDate")
    parent_patent_number: str = Field(alias="patentNumberText")
    parent_status: str = Field(alias="applicationStatus")
    relationship: RelationshipStr = Field(alias="applicationStatusDescription")


class ChildApplication(PEDSBaseModel):
    child_appl_id: str = Field(alias="claimApplicationNumberText")
    parent_appl_id: str = Field(alias="applicationNumberText")
    child_app_filing_date: MDYDate = Field(alias="filingDate")
    child_patent_number: str = Field(alias="patentNumberText")
    child_status: str = Field(alias="applicationStatus")
    relationship: RelationshipStr = Field(alias="applicationStatusDescription")


class ForeignPriority(PEDSBaseModel):
    priority_claim: str
    country_name: str
    filing_date: MDYDate


class AttorneyOrAgent(PEDSBaseModel):
    application_id: Optional[str] = None
    registration_no: Optional[str] = None
    full_name: str
    phone_num: str
    reg_status: str


class Inventor(PEDSBaseModel):
    name: str
    address: str
    rank_no: int


class Applicant(Inventor):
    cust_no: str = None


class USApplication(PEDSBaseModel):
    appl_id: str
    app_filing_date: DateTimeAsDate
    app_exam_name: Optional[str] = None
    public_ind: YNBool
    inventor_name: Optional[str] = None
    app_early_pub_number: Optional[str] = None
    app_early_pub_date: Optional[DateTimeAsDate] = None
    patent_number: Optional[str] = None
    patent_issue_date: Optional[DateTimeAsDate] = None
    app_location: Optional[str] = None
    app_grp_art_number: Optional[str] = None
    last_modified: datetime.datetime = Field(alias="LAST_MOD_TS")
    last_insert_time: datetime.datetime = Field(alias="LAST_INSERT_TIME")
    patent_title: Optional[str] = None

    app_attr_dock_number: Optional[str] = None
    app_status: Optional[str] = None
    app_status_date: Optional[DateTimeAsDate] = None
    app_type: Optional[str] = None
    app_cls_sub_cls: Optional[str] = None
    corr_name: Optional[str] = None
    corr_address: Optional[str] = None
    corr_cust_no: Optional[str] = Field(alias="corrAddrCustNo", default=None)
    transactions: List[Transactions]
    attorneys: List[AttorneyOrAgent] = Field(alias="attrnyAddr", default_factory=list)
    inventors: List[Inventor]
    applicants: List[Applicant] = Field(default_factory=list)
    pta_pte_summary: Optional[PtaOrPteSummary] = None
    pta_pte_tran_history: List[PtaOrPteTransactionHistory] = Field(default_factory=list)
    parent_continuity: List[ParentApplication] = Field(default_factory=list)
    child_continuity: List[ChildApplication] = Field(default_factory=list)
    foreign_priority: List[ForeignPriority] = Field(default_factory=list)

    @property
    def patent_center_link(self) -> str:
        return f"https://patentcenter.uspto.gov/applications/{self.appl_id}"

    @property
    def google_patents_link(self) -> Optional[str]:
        if self.patent_number is not None:
            return f"https://patents.google.com/patent/US{self.patent_number}/en"
        elif self.app_early_pub_number is not None:
            return f"https://patents.google.com/patent/{self.app_early_pub_number}/en"
        else:
            return None

    @property
    def continuity(self) -> List[Self]:
        """Returns a complete set of parents, self, and children"""
        return List(
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
    def priority_date(self) -> Optional[datetime.date]:
        """Attempts to return the priority date of the application, calculated as
        the earliest application filing date among the application's parents, or
        its own filing date if it has no parents. Does not include foreign priority
        """
        if not self.parent_continuity:
            return self.app_filing_date
        else:
            return sorted(p.parent_app_filing_date for p in self.parent_continuity)[0]

    @property
    def expiration(self) -> Optional["Expiration"]:
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
    def documents(self) -> "Iterable[Document]":
        """File History Documents from PEDS CMS"""
        return get_model("patent_client.uspto.peds.model.Document").objects.filter(appl_id=self.appl_id)

    @property
    def related_assignments(
        self,
    ) -> "Iterable[Assignment]":
        """Related Assignments from the Assignments API"""
        return get_model("patent_client.uspto.assignment.model.Assignment").objects.filter(appl_id=self.appl_id)

    @property
    def ptab_proceedings(
        self,
    ) -> "Iterable[PtabProceeding]":
        """Related PtabProceedings for this application"""
        return get_model("patent_client.uspto.ptab.model.PtabProceeding").objects.filter(appl_id=self.appl_id)

    @property
    def patent(self) -> "Optional[Patent]":
        """Fulltext version of the patent - If Available"""
        return get_model("patent_client.uspto.fulltext.patent.model.Patent").objects.get(
            publication_number=self.patent_number
        )

    @property
    def publication(
        self,
    ) -> "Optional[PublishedApplication]":
        """Fulltext version of the Publication - If Available"""
        return get_model("patent_client.uspto.public_search.model.PublishedApplication").objects.get(
            publication_number=self.publication_number,
        )

    @property
    def inpadoc_patent(
        self,
    ) -> "Optional[InpadocBiblio]":
        """Fulltext version of the patent - If Available"""
        return get_model("patent_client.epo.ops.published.model.InpadocBiblio").objects.get(
            publication_number=f"US{self.patent_number}",
        )

    @property
    def inpadoc_publication(
        self,
    ) -> "Optional[InpadocBiblio]":
        """Fulltext version of the patent - If Available"""
        return get_model("patent_client.epo.ops.published.model.InpadocBiblio").objects.get(
            publication_number=self.app_early_pub_number,
        )

    @model_validator(mode="before")
    @classmethod
    def collect_related_fields(cls, values) -> dict:
        # Collect Correspondent Data
        correspondent_name_fields = ["corrAddrNameLineOne", "corrAddrNameLineTwo", "corrAddrNameLineThree"]
        values["corrName"] = " ".join([values[field] for field in correspondent_name_fields if field in values])
        correspondent_adddress_lines = "\n".join(
            values[f] for f in ("corrAddrStreetLineOne", "corrAddrStreetLineTwo") if f in values
        )
        correspondent_address_last_line = f"{values.get('corrAddrCity', '')}, {values.get('corrAddrGeoRegionCode', '')} {values.get('corrAddrPostalCode', '')}"
        if "corrAddrCountryName" in values:
            correspondent_address_last_line += f" ({values['corrAddrCountryName']})"
        values["corrAddress"] = "\n".join([correspondent_adddress_lines, correspondent_address_last_line])
        # Collect PTA/PTE Data
        pta_pte_name_fields = (
            "totalPtoDays",
            "ptaPteInd",
            "applDelay",
            "cDelay",
            "ptoAdjustments",
            "overlapDelay",
            "aDelay",
            "bDelay",
            "ptoDelay",
        )
        pta_pte_summary = {k: values[k] for k in pta_pte_name_fields if k in values}
        if pta_pte_summary:
            values["ptaPteSummary"] = pta_pte_summary
        # Collect Inventor Names and Addresses
        for inventor in values["inventors"]:
            inventor["name"] = f"{inventor['nameLineOne']}; {inventor['nameLineTwo']} {inventor['suffix']}".strip()
            inventor["address"] = (
                "\n".join([inventor["streetOne"], inventor["streetTwo"]])
                + "\n"
                + f"{inventor['city']}{inventor['geoCode']} {inventor['country']}"
            )
        for applicant in values.get("applicants", list()):
            applicant["name"] = f"{applicant['nameLineOne']}; {applicant['nameLineTwo']} {applicant['suffix']}".strip()
            applicant["address"] = (
                "\n".join([applicant["streetOne"], applicant["streetTwo"]])
                + "\n"
                + f"{applicant['city']}{applicant['geoCode']} {applicant['country']}"
            )

        return values


class Expiration(BaseModel):
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


class Document(PEDSBaseModel):
    application_number_text: str
    mail_room_date: DateTimeAsDate
    document_code: str
    document_description: str
    document_category: str
    access_level_category: str
    document_identifier: str
    page_count: int
    pdf_url: Optional[str] = None

    def download(self, path: Optional[str | Path]) -> Path:
        return run_sync(self.adownload(path=path))

    async def adownload(self, path: Optional[str | Path]) -> Path:
        if self.pdf_url is None:
            raise ValueError("No PDF URL available")
        full_url = f"https://ped.uspto.gov/api/queries/cms/{self.pdf_url}"
        out_path = await session.adownload(full_url, path=path)
        return out_path

    @property
    def application(self) -> USApplication:
        return run_sync(self.aapplication)

    @property
    async def aapplication(self) -> USApplication:
        return await get_model("patent_client.uspto.peds.model.USApplication").objects.aget(
            appl_id=self.application_number_text
        )


class PedsPage(PEDSBaseModel):
    num_found: int = Field(validation_alias=AliasPath("queryResults", "searchResponse", "response", "numFound"))
    applications: List[USApplication] = Field(
        validation_alias=AliasPath("queryResults", "searchResponse", "response", "docs")
    )
