import datetime
from pathlib import Path
from typing import *

from patent_client.util.asyncio_util import run_sync
from patent_client.util.base.related import get_model
from patent_client.util.pydantic_util import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

MDYDate = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y").date())]
OptionalStrList = Annotated[List[str], BeforeValidator(lambda x: x if isinstance(x, list) else list())]


class GlobalDossierBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        anystr_strip_whitespace=True,
    )


class GlobalDossierPublication(GlobalDossierBaseModel):
    pub_country: Optional[str] = None
    pub_num: Optional[str] = None
    kind_code: Optional[str] = None
    pub_date: Optional[MDYDate] = Field(alias="pubDateStr")


class GlobalDossierPriorityClaim(GlobalDossierBaseModel):
    country: Optional[str] = None
    doc_number: Optional[str] = None
    kind_code: Optional[str] = None


class GlobalDossierDocumentNumber(GlobalDossierBaseModel):
    country: Optional[str] = None
    doc_number: Optional[str] = None
    format: Optional[str] = None
    date: Optional[MDYDate] = None
    kind_code: Optional[str] = None


class GlobalDossierApplication(GlobalDossierBaseModel):
    app_num: Optional[str] = None
    app_date: Optional[MDYDate] = Field(alias="appDateStr")
    country_code: Optional[str] = None
    kind_code: Optional[str] = None
    doc_num: Optional["GlobalDossierDocumentNumber"] = None
    title: Optional[str] = None
    applicant_names: OptionalStrList = Field(default_factory=list)
    ip_5: Optional[bool] = Field(alias="ip5")
    priority_claim_list: "List[GlobalDossierPriorityClaim]" = Field(default_factory=list)
    pub_list: "List[GlobalDossierPublication]" = Field(default_factory=list)

    def __repr__(self):
        return f"GlobalDossierApplication(app_num={self.app_num}, country_code={self.country_code})"

    @property
    def document_list(self):
        return get_model("patent_client.uspto.global_dossier.model.DocumentList").objects.get(
            self.country_code, self.app_num, self.kind_code
        )

    @property
    def documents(self):
        return (
            get_model("patent_client.uspto.global_dossier.model.DocumentList")
            .objects.get(self.country_code, self.app_num, self.kind_code)
            .docs
        )

    @property
    def office_actions(self):
        return (
            get_model("patent_client.uspto.global_dossier.model.DocumentList")
            .objects.get(self.country_code, self.app_num, self.kind_code)
            .office_action_docs
        )

    @property
    def us_application(self):
        if self.country_code != "US":
            raise ValueError(f"Global Dossier Application is not a US Application! {self}")
        return get_model("patent_client.uspto.peds.model.USApplication").objects.get(self.app_num)

    @property
    def us_publication(self):
        if self.country_code != "US":
            raise ValueError(f"Global Dossier Application is not a US Application! {self}")
        pub = list(p for p in self.pub_list if p.kind_code == "A1")
        if len(pub) > 1:
            raise ValueError("More than one US publication for application!")
        return get_model("patent_client.uspto.public_search.model.PublishedApplication").objects.get(pub[0].pub_num)

    @property
    def us_patent(self):
        if self.country_code != "US":
            raise ValueError(f"Global Dossier Application is not a US Application! {self}")
        pat = list(p for p in self.pub_list if p.kind_code in ("A", "B1", "B2"))
        if len(pat) > 1:
            raise ValueError("More than one US patent for application!")
        return get_model("patent_client.uspto.public_search.model.Patent").objects.get(pat[0].pub_num)

    @property
    def us_assignments(self):
        if self.country_code != "US":
            raise ValueError(f"Global Dossier Application is not a US Application! {self}")
        return get_model("patent_client.uspto.assignment.model.Assignment").objects.filter(appl_id=self.app_num)


TextBool = Annotated[bool, BeforeValidator(lambda x: x == "true")]


class GlobalDossier(GlobalDossierBaseModel):
    country: Optional[str] = None
    internal: Optional[TextBool] = None
    corr_app_num: Optional[str] = None
    id: Optional[str] = None
    type: Optional[str] = None
    applications: List[GlobalDossierApplication] = Field(default_factory=list, alias="list")

    def __repr__(self):
        return f"GlobalDossier(id={self.id}, type={self.type}, country={self.country})"


class Document(GlobalDossierBaseModel):
    doc_number: Optional[str] = None
    country: Optional[str] = None
    doc_code: Optional[str] = None
    doc_desc: Optional[str] = None
    doc_id: Optional[str] = None
    date: Optional[MDYDate] = Field(alias="legalDateStr")
    doc_format: Optional[str] = None
    pages: Optional[int] = Field(alias="numberOfPages")
    doc_code_desc: Optional[str] = None
    doc_group_code: Optional[str] = None
    shareable: Optional[bool] = None

    def download(self, filename="", path="."):
        return run_sync(self.adownload(filename, path))

    async def adownload(self, filename="", path="."):
        from .manager import global_dossier_api

        out_path = Path(path).expanduser() / (
            f'{self.date.isoformat()} - {self.doc_desc.replace("/", "_")}.pdf' if not filename else filename
        )
        return await global_dossier_api.get_document(self.country, self.doc_number, self.doc_id, out_path=out_path)


class DocumentList(GlobalDossierBaseModel):
    title: Optional[str] = None
    doc_number: Optional[str] = None
    country: Optional[str] = None
    message: Optional[str] = None
    applicant_names: "List[str]" = Field(default_factory=list)
    office_action_count: Optional[int] = Field(alias="oaIndCount")
    docs: List[Document] = Field(default_factory=list)
    office_action_docs: List[Document] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def annotate_docs_and_office_actions(cls, values):
        update_dict = {
            "country": values["country"],
            "docNumber": values["docNumber"],
        }
        for doc in values["docs"]:
            doc.update(update_dict)
        for doc in values["officeActionDocs"]:
            doc.update(update_dict)
        return values
