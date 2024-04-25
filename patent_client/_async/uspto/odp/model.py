import datetime
from enum import Enum
from typing import Any, List, Optional

from async_property import async_property
from async_property.base import AsyncPropertyDescriptor
from pydantic import AliasPath, BeforeValidator, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from patent_client.util.pydantic_util import BaseModel


class BaseODPModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, ignored_types=(AsyncPropertyDescriptor,)
    )


# Common


class Address(BaseODPModel):
    city_name: Optional[str] = Field(alias="cityName", default=None)
    geographic_region_name: Optional[str] = Field(
        alias="geographicRegionName", default=None
    )
    geographic_region_code: Optional[str] = Field(
        alias="geographicRegionCode", default=None
    )
    country_code: Optional[str] = Field(alias="countryCode", default=None)
    postal_code: Optional[str] = Field(alias="postalCode", default=None)
    country_name: Optional[str] = Field(alias="countryName", default=None)
    address_line_one_text: Optional[str] = Field(
        alias="addressLineOneText", default=None
    )
    address_line_two_text: Optional[str] = Field(
        alias="addressLineTwoText", default=None
    )
    name_line_one_text: Optional[str] = Field(alias="nameLineOneText", default=None)
    name_line_two_text: Optional[str] = Field(alias="nameLineTwoText", default=None)
    postal_address_category: Optional[str] = Field(
        alias="postalAddressCategory", default=None
    )
    correspondent_name_text: Optional[str] = Field(
        alias="correspondentNameText", default=None
    )


# Continuity


class Relationship(BaseODPModel):
    application_status_code: int = Field()
    claim_type_code: str = Field(alias="claimParentageTypeCode")
    filing_date: datetime.date
    application_status_description: str = Field(
        alias="applicationStatusDescriptionText"
    )
    claim_type_description: str = Field(alias="claimParentageTypeCodeDescription")
    parent_application_id: str = Field(alias="parentApplicationNumberText")
    child_application_id: str = Field(alias="childApplicationNumberText")


class Continuity(BaseODPModel):
    count: int
    request_identifier: str
    parent_continuity: Optional[list[Relationship]] = Field(
        alias=AliasPath(["patentBag", 0, "continuityBag", "parentContinuityBag"]),
        default=None,
    )
    child_continuity: Optional[list[Relationship]] = Field(
        alias=AliasPath(["patentBag", 0, "continuityBag", "childContinuityBag"]),
        default=None,
    )


# Documents


class DownloadOption(BaseODPModel):
    mime_type_identifier: str
    download_url: str
    pages: int = Field(alias="pageTotalQuantity")


class Document(BaseODPModel):
    appl_id: str = Field(alias="applicationNumberText")
    mail_date: datetime.datetime = Field(alias="officialDate")
    document_identifier: str = Field(alias="documentIdentifier")
    document_code: str = Field(alias="documentCode")
    document_code_description: str = Field(alias="documentCodeDescriptionText")
    direction_category: str = Field(alias="directionCategory")
    download_option_bag: list[dict] = Field(alias="downloadOptionBag")
    
    async def download(self, type="PDF", out_path=None):
        from .manager import api
        try:
            url = next(u for u in self.download_option_bag if u["mimeTypeIdentifier"] == type)["downloadUrl"]
        except StopIteration:
            raise ValueError(f"No download URL found for this document type: {type}")
        if out_path is None:
            out_path = f"{self.appl_id} - {self.mail_date.date()} - {self.document_code} - {self.document_code_description}.{type.lower()}".replace("/", "-")
        return await api.client.download(url, "GET", path=out_path)


# Assignment


class Assignor(BaseODPModel):
    execution_date: datetime.date = Field(alias="executionDate")
    assignor_name: str = Field(alias="assignorName")


class AssigneeAddress(BaseODPModel):
    city_name: str = Field(alias="cityName")
    geographic_region_code: str = Field(alias="geographicRegionCode")
    postal_code: str = Field(alias="postalCode")
    address_line_one_text: str = Field(alias="addressLineOneText")


class Assignee(BaseODPModel):
    assignee_address: AssigneeAddress = Field(alias="assigneeAddress")
    assignee_name_text: str = Field(alias="assigneeNameText")


class Assignment(BaseODPModel):
    assignment_received_date: datetime.date = Field(alias="assignmentReceivedDate")
    frame_number: str = Field(alias="frameNumber")
    page_number: int = Field(alias="pageNumber")
    reel_number_frame_number: str = Field(alias="reelNumber/frameNumber")
    assignment_recorded_date: datetime.date = Field(alias="assignmentRecordedDate")
    conveyance_text: str = Field(alias="conveyanceText")
    assignment_mailed_date: datetime.date = Field(alias="assignmentMailedDate")
    reel_number: str = Field(alias="reelNumber")
    assignor_bag: list[Assignor] = Field(alias="assignorBag")
    assignee_bag: list[Assignee] = Field(alias="assigneeBag")
    correspondence_address: list[Address] = Field(alias="correspondenceAddress")


# Foreign Priority


class ForeignPriority(BaseODPModel):
    priority_number_text: str = Field(alias="priorityNumberText")
    filing_date: datetime.date = Field(alias="filingDate")
    country_name: str = Field(alias="countryName")


# Attorney


class TelecommunicationAddress(BaseODPModel):
    telecommunication_number: str = Field(alias="telecommunicationNumber")
    usage_type_category: str = Field(alias="usageTypeCategory")


class Attorney(BaseODPModel):
    active_indicator: str = Field(alias="activeIndicator")
    first_name: Optional[str] = Field(alias="firstName", default=None)
    last_name: Optional[str] = Field(alias="lastName", default=None)
    registration_number: str = Field(alias="registrationNumber")
    attorney_address_bag: list[Address] = Field(alias="attorneyAddressBag")
    telecommunication_address_bag: list[TelecommunicationAddress] = Field(
        alias="telecommunicationAddressBag"
    )
    registered_practitioner_category: str = Field(
        alias="registeredPractitionerCategory"
    )
    name_suffix: Optional[str] = Field(alias="nameSuffix", default=None)


class CustomerNumber(BaseODPModel):
    attorneys: list[Attorney] = Field(alias="attorneyBag")
    customer_number: Optional[str] = Field(
        alias=AliasPath("customerNumber", "patronIdentifier")
    )
    address: Optional[Address] = Field(
        alias=AliasPath("customerNumber", "powerOfAttorneyAddressBag", 0)
    )


# Transactions


class Transaction(BaseODPModel):
    recorded_date: datetime.date = Field(alias="recordedDate")
    transaction_code: str = Field(alias="caseActionCode")
    transaction_description: str = Field(alias="caseActionDescriptionText")


# Adjustment Data
class TermAdjustmentHistory(BaseODPModel):
    applicant_day_delay_quantity: int = Field(alias="applicantDayDelayQuantity")
    start_sequence_number: float = Field(alias="startSequenceNumber")
    case_action_description_text: str = Field(alias="caseActionDescriptionText")
    case_action_sequence_number: float = Field(alias="caseActionSequenceNumber")
    action_date: datetime.date = Field(alias="actionDate")


class TermAdjustment(BaseODPModel):
    applicant_day_delay_quantity: Optional[int] = Field(
        alias="applicantDayDelayQuantity", default=None
    )
    overlapping_day_quantity: Optional[int] = Field(
        alias="overlappingDayQuantity", default=None
    )
    filing_date: Optional[datetime.date] = Field(alias="filingDate", default=None)
    c_delay_quantity: Optional[int] = Field(alias="cDelayQuantity", default=None)
    adjustment_total_quantity: Optional[int] = Field(
        alias="adjustmentTotalQuantity", default=None
    )
    b_delay_quantity: Optional[int] = Field(alias="bDelayQuantity", default=None)
    grant_date: Optional[datetime.date] = Field(alias="grantDate", default=None)
    a_delay_quantity: Optional[int] = Field(alias="aDelayQuantity", default=None)
    non_overlapping_day_quantity: Optional[int] = Field(
        alias="nonOverlappingDayQuantity", default=None
    )
    ip_office_day_delay_quantity: Optional[int] = Field(
        alias="ipOfficeDayDelayQuantity", default=None
    )
    history: Optional[list[TermAdjustmentHistory]] = Field(
        alias="patentTermAdjustmentHistoryDataBag", default=None
    )


# Application Object

YNBool = Annotated[bool, BeforeValidator(lambda v: v == "Y")]


class Inventor(BaseODPModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    full_name: str = Field(alias="inventorNameText")
    addresses: list[Address] = Field(alias="correspondenceAddressBag")


class Applicant(BaseODPModel):
    applicant_name: str = Field(alias="applicantNameText")
    addresses: list[Address] = Field(alias="correspondenceAddressBag")
    app_status_code: int = Field(alias="applicationStatusCode")
    app_status: str = Field(alias="applicationStatusDescriptionText")


class USApplicationBiblio(BaseODPModel):
    aia_indicator: YNBool = Field(alias="firstInventorToFileIndicator")
    app_filing_date: datetime.date = Field(alias="filingDate")
    inventors: list[Inventor] = Field(alias="inventorBag")
    customer_number: int = Field(alias="customerNumber")
    group_art_unit: str = Field(alias="groupArtUnitNumber")
    invention_title: str = Field(alias="inventionTitle")
    correspondence_address: list[Address] = Field(alias="correspondenceAddressBag")
    app_conf_num: int = Field(alias="applicationConfirmationNumber")
    atty_docket_num: str = Field(alias="docketNumber")
    appl_id: str = Field(alias="applicationNumberText")
    first_inventor_name: str = Field(alias="firstInventorName")
    first_applicant_name: str = Field(alias="firstApplicantName")
    cpc_classifications: list[str] = Field(alias="cpcClassificationBag")
    entity_status: str = Field(alias="businessEntityStatusCategory")
    app_early_pub_number: Optional[str] = Field(alias="earliestPublicationNumber")

    @async_property
    async def bibliographic_data(self) -> "USApplicationBiblio":
        return await self._get_model(".model.USApplicationBiblio").objects.get(
            appl_id=self.appl_id
        )

    @async_property
    async def application(self) -> "USApplication":
        return await self._get_model(".model.USApplication").objects.get(
            appl_id=self.appl_id
        )

    @async_property
    async def continuity(self) -> Continuity:
        return await self._get_model(".model.Continuity").objects.get(
            appl_id=self.appl_id
        )

    @async_property
    async def documents(self) -> list[Document]:
        return self._get_model(".model.Document").objects.filter(appl_id=self.appl_id)
    
    @async_property
    async def term_adjustment(self) -> TermAdjustment:
        return self._get_model(".model.TermAdjustment").objects.filter(appl_id=self.appl_id)
    
    @async_property
    async def assignments(self) -> list[Assignment]:
        return self._get_model(".model.Assignment").objects.filter(appl_id=self.appl_id)
    
    @async_property
    async def customer_number(self) -> CustomerNumber:
        return self._get_model(".model.CustomerNumber").objects.filter(appl_id=self.appl_id)
    
    @async_property
    async def foreign_priority(self) -> ForeignPriority:
        return self._get_model(".model.ForeignPriority").objects.filter(appl_id=self.appl_id)
    
    @async_property
    async def transactions(self) -> list[Transaction]:
        return self._get_model(".model.Transaction").objects.filter(appl_id=self.appl_id)

    # Aliases

    @async_property
    async def biblio(self) -> "USApplicationBiblio":
        return await self.bibliographic_data

    @async_property
    async def app(self) -> "USApplication":
        return await self.application

    @async_property
    async def docs(self) -> list[Document]:
        return await self.documents


class USApplication(BaseODPModel):
    aia_indicator: YNBool = Field(alias="firstInventorToFileIndicator")
    app_filing_date: datetime.date = Field(alias="filingDate")
    inventors: list[Inventor] = Field(alias="inventorBag")
    customer_number: int = Field(alias="customerNumber")
    group_art_unit: str = Field(alias="groupArtUnitNumber")
    invention_title: str = Field(alias="inventionTitle")
    correspondence_address: list[Address] = Field(alias="correspondenceAddressBag")
    app_conf_num: int = Field(alias="applicationConfirmationNumber")
    atty_docket_num: str = Field(alias="docketNumber")
    appl_id: str = Field(alias="applicationNumberText")
    first_inventor_name: str = Field(alias="firstInventorName")
    first_applicant_name: str = Field(alias="firstApplicantName")
    cpc_classifications: list[str] = Field(alias="cpcClassificationBag")
    entity_status: str = Field(alias="businessEntityStatusCategory")
    app_early_pub_number: Optional[str] = Field(alias="earliestPublicationNumber")
    
    
    app_type_code: str = Field(alias="applicationTypeCode")
    national_stage_indicator: YNBool = Field(alias="nationalStageIndicator")

    effective_filing_date: datetime.date = Field(alias="effectiveFilingDate")
    cls_sub_cls: str = Field(alias="class/subclass")
    assignments: list[Assignment] = Field(alias="assignmentBag")
    attorneys: CustomerNumber = Field(alias="recordAttorney")
    transactions: list[Transaction] = Field(alias="transactionContentBag")
    parent_applications: Optional[list[Relationship]] = Field(
        alias=AliasPath("continuityBag", "parentContinuityBag"), default=None
    )
    child_applications: Optional[list[Relationship]] = Field(
        alias=AliasPath("continuityBag", "childContinuityBag"), default=None
    )
    patent_term_adjustment: Optional[TermAdjustment] = Field(
        alias="patentTermAdjustmentData"
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_patent_term_adjustment(cls, v):
        if v["patentTermAdjustmentData"] == dict():
            v["patentTermAdjustmentData"] = None
        return v


## RESPONSE Models


class SearchResult(BaseODPModel):
    filing_date: datetime.date
    appl_id: str = Field(alias="applicationNumberText")
    invention_title: str = Field(alias="inventionTitle")
    filing_date: datetime.date = Field(alias="filingDate")
    patent_number: Optional[str] = Field(alias="patentNumber", default=None)


class SearchResponse(BaseODPModel):
    count: int
    results: list[SearchResult] = Field(alias="patentBag")
    request_id: str = Field(alias="requestIdentifier")


## Request Models


class Filter(BaseModel):
    name: str
    value: List[str]


class Range(BaseModel):
    field: str = Field(examples=["grantDate"])
    valueFrom: str = Field(examples=["2020-01-01"])
    valueTo: str = Field(examples=["2020-12-31"])

    @model_validator(mode="before")
    @classmethod
    def add_default_dates(cls, data: Any) -> Any:
        if data.get("valueFrom") is None:
            data["valueFrom"] = "1776-07-04"
        if data.get("valueTo") is None:
            data["valueTo"] = datetime.date.today().isoformat()
        return data


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
    Asc = "Asc"
    Desc = "Desc"


class Sort(BaseModel):
    field: str = Field(examples=["grantDate"])
    order: SortOrder = Field(examples=[SortOrder.desc])


class Pagination(BaseModel):
    offset: int = Field(examples=[0], default=0, ge=0)
    limit: int = Field(examples=[25], default=25, ge=1)


class SearchRequest(BaseModel):
    q: str = Field(default="")
    filters: Optional[List[Filter]] = Field(default=None)
    rangeFilters: Optional[List[Range]] = Field(default=None)
    sort: Optional[List[Sort]] = Field(default=None)
    fields: Optional[List[str]] = Field(default=None)
    pagination: Optional[Pagination] = Field(default=None)
    facets: Optional[List[str]] = Field(default=None)


class SearchGetRequest(BaseModel):
    q: str = Field(default="")
    sort: str = Field(default="filingDate")
    fields: str = Field(default="")
    offset: int = Field(default=0)
    limit: int = Field(default=25)