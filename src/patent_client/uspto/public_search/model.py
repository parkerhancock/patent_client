import datetime
from dataclasses import dataclass
from dataclasses import field

from patent_client.util.base.model import Model
from patent_client.util.base.related import get_model
from patent_client.util.claims.parser import ClaimsParser
from yankee.data import ListCollection

from . import public_search_api

claim_parser = ClaimsParser()


@dataclass
class DocumentStructure(Model):
    number_of_claims: "Optional[int]" = None
    number_of_drawing_sheets: "Optional[int]" = None
    number_of_figures: "Optional[int]" = None
    page_count: "Optional[int]" = None
    front_page_end: "Optional[int]" = None
    front_page_start: "Optional[int]" = None
    bib_start: "Optional[int]" = None
    bib_end: "Optional[int]" = None
    abstract_start: "Optional[int]" = None
    abstract_end: "Optional[int]" = None
    drawings_start: "Optional[int]" = None
    drawings_end: "Optional[int]" = None
    description_start: "Optional[int]" = None
    description_end: "Optional[int]" = None
    specification_start: "Optional[int]" = None
    specification_end: "Optional[int]" = None
    claims_end: "Optional[int]" = None
    claims_start: "Optional[int]" = None
    amend_start: "Optional[int]" = None
    amend_end: "Optional[int]" = None
    cert_correction_end: "Optional[int]" = None
    cert_correction_start: "Optional[int]" = None
    cert_reexamination_end: "Optional[int]" = None
    cert_reexamination_start: "Optional[int]" = None
    ptab_start: "Optional[int]" = None
    ptab_end: "Optional[int]" = None
    search_report_start: "Optional[int]" = None
    search_report_end: "Optional[int]" = None
    supplemental_start: "Optional[int]" = None
    supplemental_end: "Optional[int]" = None


@dataclass
class PublicSearch(Model):
    __manager__ = "patent_client.uspto.public_search.manager.PublicSearchManager"
    guid: "Optional[str]" = None

    appl_id: "Optional[str]" = None
    app_filing_date: "Optional[datetime.date]" = None
    related_appl_filing_date: "ListCollection" = field(default_factory=ListCollection)
    publication_number: "Optional[str]" = None
    kind_code: "Optional[str]" = None
    publication_date: "Optional[datetime.date]" = None
    patent_title: "Optional[str]" = None

    inventors_short: "Optional[str]" = None
    applicant_name: "ListCollection" = field(default_factory=ListCollection)
    assignee_name: "ListCollection" = field(default_factory=ListCollection)
    government_interest: "ListCollection" = field(default_factory=ListCollection)
    primary_examiner: "Optional[str]" = None
    assistant_examiner: "ListCollection" = field(default_factory=ListCollection)

    main_classification_code: "Optional[str]" = None
    cpc_additional: "Optional[str]" = None
    cpc_inventive: "Optional[str]" = None
    ipc_code: "Optional[str]" = None
    uspc_full_classification: "Optional[str]" = None

    image_file_name: "Optional[str]" = None
    image_location: "Optional[str]" = None
    document_structure: "Optional[DocumentStructure]" = None

    type: "Optional[str]" = None
    database_name: "Optional[str]" = None
    composite_id: "Optional[str]" = None
    document_id: "Optional[str]" = None
    document_size: "Optional[int]" = None
    family_identifier_cur: "Optional[int]" = None
    language_indicator: "Optional[str]" = None

    score: "Optional[float]" = None

    def __repr__(self):
        return f"PublicationBiblio(publication_number={self.publication_number}, publication_date={self.publication_date.isoformat()}, patent_title={self.patent_title})"

    @property
    def document(self):
        return get_model("patent_client.uspto.public_search.model.PatentDocument").objects.get(guid=self.guid)

    @property
    def forward_citations(self):
        return get_model("patent_client.uspto.public_search.model.PublicSearch").objects.filter(
            us_reference=self.publication_number
        )

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

    def download_images(self, path="."):
        return public_search_api.download_image(self, path)


@dataclass
class Document(Model):
    abstract: "Optional[str]" = None
    government_interest: "Optional[str]" = None
    background: "Optional[str]" = None
    description: "Optional[str]" = None
    brief: "Optional[str]" = None
    claim_statement: "Optional[str]" = None
    claims: "Optional[str]" = None


@dataclass
class UsReference(Model):
    publication_number: "Optional[str]" = None
    pub_month: "Optional[datetime.date]" = None
    patentee_name: "Optional[str]" = None
    cited_by_examiner: "Optional[bool]" = None


@dataclass
class ForeignReference(Model):
    citation_classification: "Optional[str]" = None
    citation_cpc: "Optional[str]" = None
    country_code: "Optional[str]" = None
    patent_number: "Optional[str]" = None
    pub_month: "Optional[datetime.date]" = None
    cited_by_examiner: "Optional[bool]" = None


@dataclass
class NplReference(Model):
    citation: "Optional[str]" = None
    cited_by_examiner: "Optional[bool]" = None


@dataclass
class RelatedApplication(Model):
    child_patent_country: "Optional[str]" = None
    child_patent_number: "Optional[str]" = None
    country_code: "Optional[str]" = None
    filing_date: "Optional[datetime.date]" = None
    number: "Optional[str]" = None
    parent_status_code: "Optional[str]" = None
    patent_issue_date: "Optional[datetime.date]" = None
    patent_number: "Optional[str]" = None


@dataclass
class Inventor(Model):
    name: "Optional[str]" = None
    city: "Optional[str]" = None
    country: "Optional[str]" = None
    postal_code: "Optional[str]" = None
    state: "Optional[str]" = None


@dataclass
class Applicant(Model):
    city: "Optional[str]" = None
    country: "Optional[str]" = None
    # group: "Optional[str]" = None
    name: "Optional[str]" = None
    state: "Optional[str]" = None
    zip_code: "Optional[str]" = None
    authority_type: "Optional[str]" = None


@dataclass
class Assignee(Model):
    city: "Optional[str]" = None
    country: "Optional[str]" = None
    name: "Optional[str]" = None
    postal_code: "Optional[str]" = None
    state: "Optional[str]" = None
    type_code: "Optional[str]" = None


@dataclass
class CpcCode(Model):
    cpc_class: "Optional[str]" = None
    cpc_subclass: "Optional[str]" = None
    version: "Optional[datetime.date]" = None


@dataclass
class IntlCode(Model):
    intl_class: "Optional[str]" = None
    intl_subclass: "Optional[str]" = None
    version: "Optional[datetime.date]" = None


@dataclass
class ForeignPriorityApplication(Model):
    country: "Optional[str]" = None
    app_filing_date: "Optional[datetime.date]" = None
    app_number: "Optional[str]" = None


@dataclass
class PublicSearchDocument(Model):
    guid: "Optional[str]" = None
    publication_number: "Optional[str]" = None
    publication_date: "Optional[datetime.date]" = None

    appl_id: "Optional[str]" = None
    patent_title: "Optional[str]" = None
    app_filing_date: "Optional[datetime.date]" = None
    application_type: "Optional[str]" = None
    family_identifier_cur: "Optional[int]" = None
    related_apps: "ListCollection[RelatedApplication]" = field(default_factory=ListCollection)
    foreign_priority: "ListCollection[ForeignPriorityApplication]" = field(default_factory=ListCollection)
    type: "Optional[str]" = None

    # Parties
    inventors: "ListCollection[Inventor]" = field(default_factory=ListCollection)
    inventors_short: "Optional[str]" = None
    applicants: "ListCollection[Applicant]" = field(default_factory=ListCollection)
    assignees: "ListCollection[Assignee]" = field(default_factory=ListCollection)

    group_art_unit: "Optional[str]" = None
    primary_examiner: "Optional[str]" = None
    assistant_examiner: "ListCollection" = field(default_factory=ListCollection)
    legal_firm_name: "ListCollection" = field(default_factory=ListCollection)
    attorney_name: "ListCollection" = field(default_factory=ListCollection)

    # Text Data
    document: "Optional[Document]" = None
    document_structure: "Optional[DocumentStructure]" = None

    # Image Data
    image_file_name: "Optional[str]" = None
    image_location: "Optional[str]" = None

    # Metadata
    composite_id: "Optional[str]" = None
    database_name: "Optional[str]" = None
    derwent_week_int: "Optional[int]" = None

    # References Cited
    us_references: "ListCollection[UsReference]" = field(default_factory=ListCollection)
    foreign_references: "ListCollection[ForeignReference]" = field(default_factory=ListCollection)
    npl_references: "ListCollection[NplReference]" = field(default_factory=ListCollection)

    # Classifications
    cpc_inventive: "ListCollection" = field(default_factory=ListCollection)
    cpc_additional: "ListCollection" = field(default_factory=ListCollection)

    intl_class_issued: "ListCollection[str]" = field(default_factory=ListCollection)
    intl_class_current_primary: "ListCollection[IntlClass]" = field(default_factory=ListCollection)
    intl_class_currrent_secondary: "ListCollection" = field(default_factory=ListCollection)

    us_class_current: "ListCollection[str]" = field(default_factory=ListCollection)
    us_class_issued: "ListCollection" = field(default_factory=ListCollection)

    field_of_search_us: "ListCollection" = field(default_factory=ListCollection)
    field_of_search_cpc: "ListCollection" = field(default_factory=ListCollection)

    def __repr__(self):
        return f"Publication(publication_number={self.publication_number}, publication_date={self.publication_date.isoformat()}, patent_title={self.patent_title})"

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
        return get_model("patent_client.uspto.public_search.model.PublicSearch").objects.filter(
            us_reference=self.publication_number
        )

    def download_images(self, path="."):
        return public_search_api.download_image(self, path)

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


@dataclass
class PatentBiblio(PublicSearch):
    __manager__ = "patent_client.uspto.public_search.manager.PatentBiblioManager"


@dataclass
class Patent(PublicSearchDocument):
    __manager__ = "patent_client.uspto.public_search.manager.PatentManager"


@dataclass
class PublishedApplicationBiblio(PublicSearch):
    __manager__ = "patent_client.uspto.public_search.manager.PublishedApplicationBiblioManager"


@dataclass
class PublishedApplication(PublicSearchDocument):
    __manager__ = "patent_client.uspto.public_search.manager.PublishedApplicationManager"
