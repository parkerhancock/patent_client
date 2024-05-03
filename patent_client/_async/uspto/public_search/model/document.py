from typing import List, Optional

from pydantic import Field, model_validator

from patent_client.util.claims.model import Claim
from patent_client.util.pydantic_util import BaseModel, Date

from ..convert.document import PublicSearchDocumentSchema
from .shared import ApplicationNumber, DocumentStructure, HtmlString, OptionalList


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
    claims_text: Optional[HtmlString] = Field(alias="claims_html", default=None)
    claims: List[Claim] = Field(default_factory=list)


class UsReference(BaseModel):
    publication_number: Optional[str] = None
    pub_month: Optional[Date] = None
    patentee_name: Optional[str] = None
    cited_by_examiner: Optional[bool] = None


class ForeignReference(BaseModel):
    citation_classification: Optional[str] = None
    citation_cpc: Optional[str] = None
    country_code: Optional[str] = None
    patent_number: Optional[str] = None
    pub_month: Optional[Date] = None
    cited_by_examiner: Optional[bool] = None


class NplReference(BaseModel):
    citation: Optional[str] = None
    cited_by_examiner: Optional[bool] = None


class RelatedApplication(BaseModel):
    child_patent_country: Optional[str] = None
    child_patent_number: Optional[str] = None
    country_code: Optional[str] = None
    filing_date: Optional[Date] = None
    number: Optional[str] = None
    parent_status_code: Optional[str] = None
    patent_issue_date: Optional[Date] = None
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
    version: Optional[Date] = None


class IntlCode(BaseModel):
    intl_class: Optional[str] = None
    intl_subclass: Optional[str] = None
    version: Optional[Date] = None


class ForeignPriorityApplication(BaseModel):
    country: Optional[str] = None
    app_filing_date: Optional[Date] = None
    app_number: Optional[str] = None


class PublicSearchDocument(BaseModel):
    __schema__ = PublicSearchDocumentSchema()
    guid: Optional[str] = None
    publication_number: Optional[str] = None
    publication_date: Optional[Date] = None

    appl_id: Optional[ApplicationNumber] = None
    patent_title: Optional[str] = None
    app_filing_date: Optional[Date] = None
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

    def __repr__(self):
        return f"PublicSearchDocument(publication_number={self.publication_number}, publication_date={self.publication_date}, patent_title={self.patent_title})"

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
        return self.document.claims

    @property
    def forward_citations(self):
        return self._get_model(".PublicSearchBiblio").objects.filter(
            us_reference=self.publication_number
        )

    async def download_images(self, path="."):
        from ..manager import public_search_api

        return await public_search_api.download_image(self, path)

    @property
    def application(self):
        return self._get_model("...peds.model.USApplication").objects.get(self.appl_id)

    @property
    def global_dossier(self):
        return self._get_model("...global_dossier.model.GlobalDossierApplication").objects.get(
            self.appl_id
        )

    @property
    def assignments(self):
        return self._get_model("...assignment.model.Assignment").objects.filter(
            appl_id=self.appl_id
        )

    @property
    def inpadoc(self):
        return self._get_model("...epo.ops.published.model.Inpadoc").objects.get(
            "US" + self.publication_number
        )

    @model_validator(mode="before")
    @classmethod
    def convert_xml_to_json(cls, values):
        return cls.__schema__.deserialize(values).to_dict()
