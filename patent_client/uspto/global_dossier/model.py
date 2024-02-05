import datetime
import typing as tp
from pathlib import Path

from pydantic import BeforeValidator
from pydantic import computed_field
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from patent_client._async.uspto.global_dossier import GlobalDossierApi as GlobalDossierAsyncApi
from patent_client._sync.uspto.global_dossier import GlobalDossierApi as GlobalDossierSyncApi
from patent_client.util.pydantic_util import BaseModel
from patent_client.util.related import get_model

MDYDate = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y").date())]
OptionalStrList = Annotated[list[str], BeforeValidator(lambda x: x if isinstance(x, list) else list())]


class GlobalDossierBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        str_strip_whitespace=True,
    )


class GlobalDossierPublication(GlobalDossierBaseModel):
    pub_country: tp.Optional[str] = None
    pub_num: tp.Optional[str] = None
    kind_code: tp.Optional[str] = None
    pub_date: tp.Optional[MDYDate] = Field(alias="pubDateStr")


class GlobalDossierPriorityClaim(GlobalDossierBaseModel):
    country: tp.Optional[str] = None
    doc_number: tp.Optional[str] = None
    kind_code: tp.Optional[str] = None


class GlobalDossierDocumentNumber(GlobalDossierBaseModel):
    country: tp.Optional[str] = None
    doc_number: tp.Optional[str] = None
    format: tp.Optional[str] = None
    date: tp.Optional[MDYDate] = None
    kind_code: tp.Optional[str] = None


class GlobalDossierApplication(GlobalDossierBaseModel):
    app_num: tp.Optional[str] = None
    app_date: tp.Optional[MDYDate] = Field(alias="appDateStr")
    country_code: tp.Optional[str] = None
    kind_code: tp.Optional[str] = None
    doc_num: tp.Optional["GlobalDossierDocumentNumber"] = None
    title: tp.Optional[str] = None
    applicant_names: OptionalStrList = Field(default_factory=list)
    ip_5: tp.Optional[bool] = Field(alias="ip5")
    priority_claim_list: list[GlobalDossierPriorityClaim] = Field(default_factory=list)
    pub_list: list[GlobalDossierPublication] = Field(default_factory=list)

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

    """
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
    """


TextBool = Annotated[bool, BeforeValidator(lambda x: x == "true")]


class GlobalDossier(GlobalDossierBaseModel):
    country: tp.Optional[str] = None
    internal: tp.Optional[TextBool] = None
    corr_app_num: tp.Optional[str] = None
    id: tp.Optional[str] = None
    type: tp.Optional[str] = None
    applications: list[GlobalDossierApplication] = Field(default_factory=list, alias="list")

    def __repr__(self):
        return f"GlobalDossier(id={self.id}, type={self.type}, country={self.country})"


class Document(GlobalDossierBaseModel):
    doc_number: tp.Optional[str] = None
    country: tp.Optional[str] = None
    doc_code: tp.Optional[str] = None
    doc_desc: tp.Optional[str] = None
    doc_id: tp.Optional[str] = None
    date: tp.Optional[MDYDate] = Field(alias="legalDateStr")
    doc_format: tp.Optional[str] = None
    pages: tp.Optional[int] = Field(alias="numberOfPages")
    doc_code_desc: tp.Optional[str] = None
    doc_group_code: tp.Optional[str] = None
    shareable: tp.Optional[bool] = None

    def download(self, filename="", path="."):
        out_path = Path(path).expanduser() / (
            f'{self.date.isoformat()} - {self.doc_desc.replace("/", "_")}.pdf' if not filename else filename
        )
        return GlobalDossierSyncApi.get_document(self.country, self.doc_number, self.doc_id, out_path)

    async def adownload(self, filename="", path="."):
        out_path = Path(path).expanduser() / (
            f'{self.date.isoformat()} - {self.doc_desc.replace("/", "_")}.pdf' if not filename else filename
        )
        return await GlobalDossierAsyncApi.get_document(self.country, self.doc_number, self.doc_id, out_path)


class DocumentList(GlobalDossierBaseModel):
    title: tp.Optional[str] = None
    doc_number: tp.Optional[str] = None
    country: tp.Optional[str] = None
    message: tp.Optional[str] = None
    applicant_names: list[str] = Field(default_factory=list)
    # office_action_count: tp.Optional[int] = Field(alias="oaIndCount")
    # This field is occasionally incorrect, so we'll just count the office actions ourselves
    docs: list[Document] = Field(default_factory=list)
    office_action_docs: list[Document] = Field(default_factory=list)

    @computed_field
    def office_action_count(self) -> int:
        return len(self.office_action_docs)

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
