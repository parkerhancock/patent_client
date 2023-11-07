import datetime
import re
from typing import List
from typing import Optional

import lxml.html as ETH
from patent_client.util.asyncio_util import run_sync
from patent_client.util.base.related import get_model
from patent_client.util.claims.parser import ClaimsParser
from patent_client.util.pydantic_util import BaseModel
from pydantic import BeforeValidator
from pydantic import Field
from pydantic import model_validator
from typing_extensions import Annotated

from ..convert.document import PublicSearchDocumentSchema

claim_parser = ClaimsParser()
from .shared import ApplicationNumber, DocumentStructure, OptionalList

newline_re = re.compile(r"<br />\s*")
bad_break_re = re.compile(r"<br />\s+")


def html_to_text(html):
    html = newline_re.sub("\n\n", html)
    # html = bad_break_re.sub(" ", html)
    return "".join(ETH.fromstring(html).itertext())


HtmlString = Annotated[str, BeforeValidator(html_to_text)]


class Document(BaseModel):
    abstract_html: Optional[str] = None
    abstract: Optional[HtmlString] = Field(alias="abstract_html", default=None)
    government_interest: Optional[str] = None
    background_html: Optional[str] = Field(alias="background_html", default=None)
    background: Optional[HtmlString] = Field(alias="background_html", default=None)
    description_html: Optional[str] = None
    description: Optional[HtmlString] = Field(alias="description_html", default=None)
    brief_html: Optional[str] = None
    brief: Optional[HtmlString] = Field(alias="brief_html", default=None)
    claim_statement: Optional[str] = None
    claims_html: Optional[str] = None
    claims: Optional[HtmlString] = Field(alias="claims_html", default=None)


class UsReference(BaseModel):
    publication_number: Optional[str]
    pub_month: Optional[datetime.date]
    patentee_name: Optional[str]
    cited_by_examiner: Optional[bool]


class ForeignReference(BaseModel):
    citation_classification: Optional[str]
    citation_cpc: Optional[str]
    country_code: Optional[str]
    patent_number: Optional[str]
    pub_month: Optional[datetime.date]
    cited_by_examiner: Optional[bool]


class NplReference(BaseModel):
    citation: Optional[str] = None
    cited_by_examiner: Optional[bool] = None


class RelatedApplication(BaseModel):
    child_patent_country: Optional[str] = None
    child_patent_number: Optional[str] = None
    country_code: Optional[str] = None
    filing_date: Optional[datetime.date] = None
    number: Optional[str] = None
    parent_status_code: Optional[str] = None
    patent_issue_date: Optional[datetime.date] = None
    patent_number: Optional[str] = None


class Inventor(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None


class Applicant(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    # group: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    authority_type: Optional[str] = None


class Assignee(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    name: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None
    type_code: Optional[str] = None


class CpcCode(BaseModel):
    cpc_class: Optional[str] = None
    cpc_subclass: Optional[str] = None
    version: Optional[datetime.date] = None


class IntlCode(BaseModel):
    intl_class: Optional[str] = None
    intl_subclass: Optional[str] = None
    version: Optional[datetime.date] = None


class ForeignPriorityApplication(BaseModel):
    country: Optional[str] = None
    app_filing_date: Optional[datetime.date] = None
    app_number: Optional[str] = None


class PublicSearchDocument(BaseModel):
    __schema__ = PublicSearchDocumentSchema()
    guid: Optional[str] = None
    publication_number: Optional[str] = None
    publication_date: Optional[datetime.date] = None

    appl_id: Optional[ApplicationNumber] = None
    patent_title: Optional[str] = None
    app_filing_date: Optional[datetime.date] = None
    application_type: Optional[str] = None
    family_identifier_cur: Optional[int] = None
    related_apps: List[RelatedApplication] = Field(default_factory=list)
    foreign_priority: List[ForeignPriorityApplication] = Field(default_factory=list)
    type: Optional[str] = None

    # Parties
    inventors: List[Inventor] = Field(default_factory=list)
    inventors_short: Optional[str] = None
    applicants: List[Applicant] = Field(default_factory=list)
    assignees: List[Assignee] = Field(default_factory=list)

    group_art_unit: Optional[str] = None
    primary_examiner: Optional[str] = None
    assistant_examiner: Optional[List[str]] = Field(default_factory=list)
    legal_firm_name: Optional[List[str]] = Field(default_factory=list)
    attorney_name: Optional[List[str]] = Field(default_factory=list)

    # Text Data
    document: Optional[Document] = None
    document_structure: Optional[DocumentStructure] = None

    # Image Data
    image_file_name: Optional[str] = None
    image_location: Optional[str] = None

    # Metadata
    composite_id: Optional[str] = None
    database_name: Optional[str] = None
    derwent_week_int: Optional[int] = None

    # References Cited
    us_references: OptionalList[UsReference] = Field(default_factory=list)
    foreign_references: OptionalList[ForeignReference] = Field(default_factory=list)
    npl_references: OptionalList[NplReference] = Field(default_factory=list)

    # Classifications
    cpc_inventive: OptionalList = Field(default_factory=list)
    cpc_additional: OptionalList = Field(default_factory=list)

    intl_class_issued: OptionalList[str] = Field(default_factory=list)
    intl_class_current_primary: OptionalList[IntlCode] = Field(default_factory=list)
    intl_class_currrent_secondary: OptionalList[IntlCode] = Field(default_factory=list)

    us_class_current: OptionalList[str] = Field(default_factory=list)
    us_class_issued: OptionalList[str] = Field(default_factory=list)

    field_of_search_us: OptionalList[str] = Field(default_factory=list)
    field_of_search_cpc: OptionalList[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def convert(cls, values):
        return PublicSearchBiblioConvert.convert(values)

    @property
    def abstract(self):
        return self.document.abstract

    @property
    def description(self):
        sections = (
            "government_interest",
            "background",
            "brief",
            "description",
        )
        section_text = tuple(getattr(self.document, s) for s in sections)
        return "\n\n".join(s for s in section_text if s)

    @property
    def claims_text(self):
        return self.document.claims

    @property
    def claims(self):
        return claim_parser.parse(self.document.claims)

    @property
    def forward_citations(self):
        return get_model("patent_client.uspto.public_search.model.PublicSearchBiblio").objects.filter(
            us_reference=self.publication_number
        )

    def download_images(self, path="."):
        return run_sync(self.adownload_images(path))

    async def adownload_images(self, path="."):
        from ..manager import public_search_api

        return await public_search_api.download_image(self, path)

    @property
    def application(self):
        return get_model("patent_client.uspto.peds.model.USApplication").objects.get(self.appl_id)

    @property
    def global_dossier(self):
        return get_model("patent_client.uspto.global_dossier.model.GlobalDossierApplication").objects.get(self.appl_id)

    @property
    def assignments(self):
        return get_model("patent_client.uspto.assignment.model.Assignment").objects.filter(appl_id=self.appl_id)

    @property
    def inpadoc(self):
        return get_model("patent_client.epo.ops.published.model.Inpadoc").objects.get("US" + self.publication_number)

    @model_validator(mode="before")
    @classmethod
    def convert(cls, values):
        return cls.__schema__.deserialize(values).to_dict()
