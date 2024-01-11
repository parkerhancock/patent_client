import datetime
from typing import Optional

from pydantic import AliasPath
from pydantic import Field
from pydantic import model_validator

from ..convert.biblio import PublicSearchBiblioPageSchema
from .shared import ApplicationNumber
from .shared import DateTimeAsDate
from .shared import DocumentStructure
from .shared import HtmlString
from .shared import OptionalList
from patent_client._async.uspto.public_search import PublicSearchApi as PublicSearchAsyncApi
from patent_client._sync.uspto.public_search import PublicSearchApi as PublicSearchSyncApi
from patent_client.util.pydantic_util import BaseModel
from patent_client.util.related import get_model


class PublicSearchBiblio(BaseModel):
    guid: Optional[str] = None
    publication_number: Optional[str] = None
    publication_date: Optional[datetime.date] = None
    patent_title: Optional[HtmlString] = None
    type: Optional[str] = None
    main_classification_code: Optional[str] = None
    applicant_names: OptionalList[str] = Field(alias="applicant_name", default_factory=list)
    assignee_names: OptionalList[str] = Field(alias="assignee_name", default_factory=list)
    uspc_full_classification: OptionalList[str] = Field(default_factory=list)
    ipc_code: OptionalList[str] = Field(default_factory=list)
    cpc_additional: OptionalList[str] = Field(default_factory=list)
    app_filing_date: Optional[datetime.date] = None
    related_appl_filing_date: OptionalList[DateTimeAsDate] = Field(alias="relatedApplFilingDate", default_factory=list)
    primary_examiner: Optional[str] = None
    assistant_examiner: Optional[str] = Field(alias=AliasPath("assistant_examiner", 0), default=None)
    appl_id: Optional[ApplicationNumber] = None
    document_structure: DocumentStructure

    def __repr__(self):
        return f"PublicSearcBiblio(publication_number={self.publication_number}, publication_date={self.publication_date}, patent_title={self.patent_title})"

    @property
    def document(self):
        return get_model("patent_client.uspto.public_search.model.PublicSearchDocument").objects.get(guid=self.guid)

    @property
    def forward_citations(self):
        return get_model("patent_client.uspto.public_search.model.PublicSearchBiblio").objects.filter(
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
        return PublicSearchSyncApi.download_images(
            self.guid, self.image_location, self.type, self.document_structure.page_count, path
        )

    async def adownload_images(self, path="."):
        return await PublicSearchAsyncApi.download_images(
            self.guid, self.image_location, self.type, self.document_structure.page_count, path
        )


class PublicSearchBiblioPage(BaseModel):
    __schema__ = PublicSearchBiblioPageSchema()
    num_found: int
    per_page: int
    page: int
    docs: OptionalList[PublicSearchBiblio] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def run_convert(cls, values):
        return cls.__schema__.deserialize(values).to_dict()
