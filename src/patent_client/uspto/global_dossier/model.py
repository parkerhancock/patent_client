import datetime
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import *

from patent_client.util.asyncio_util import run_sync
from patent_client.util.base.model import Model
from patent_client.util.base.related import get_model
from yankee.data import ListCollection

from .api import GlobalDossierAsyncApi

global_dossier_async_api = GlobalDossierAsyncApi()


@dataclass
class GlobalDossierPublication(Model):
    pub_country: Optional[str] = None
    pub_num: Optional[str] = None
    kind_code: Optional[str] = None
    pub_date: Optional[datetime.date] = None


@dataclass
class GlobalDossierPriorityClaim(Model):
    country: Optional[str] = None
    doc_number: Optional[str] = None
    kind_code: Optional[str] = None


@dataclass
class GlobalDossierDocumentNumber(Model):
    country: Optional[str] = None
    doc_number: Optional[str] = None
    format: Optional[str] = None
    date: Optional[datetime.date] = None
    kind_code: Optional[str] = None


@dataclass
class GlobalDossierApplication(Model):
    __manager__ = "patent_client.uspto.global_dossier.manager.GlobalDossierApplicationManager"
    app_num: Optional[str] = None
    app_date: Optional[datetime.date] = None
    country_code: Optional[str] = None
    kind_code: Optional[str] = None
    doc_num: Optional["GlobalDossierDocumentNumber"] = None
    title: Optional[str] = None
    applicant_names: Optional[str] = None
    ip_5: Optional[bool] = None
    priority_claim_list: "ListCollection[GlobalDossierPriorityClaim]" = field(default_factory=ListCollection)
    pub_list: "ListCollection[GlobalDossierPublication]" = field(default_factory=ListCollection)

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


@dataclass
class GlobalDossier(Model):
    __manager__ = "patent_client.uspto.global_dossier.manager.GlobalDossierManager"
    country: Optional[str] = None
    internal: Optional[bool] = None
    corr_app_num: Optional[str] = None
    id: Optional[str] = None
    type: Optional[str] = None
    applications: "ListCollection[GlobalDossierApplication]" = field(default_factory=ListCollection)

    def __repr__(self):
        return f"GlobalDossier(id={self.id}, type={self.type}, country={self.country})"


@dataclass
class Document(Model):
    doc_number: Optional[str] = None
    country: Optional[str] = None
    doc_code: Optional[str] = None
    doc_desc: Optional[str] = None
    doc_id: Optional[str] = None
    date: Optional[datetime.date] = None
    doc_format: Optional[str] = None
    pages: Optional[int] = None
    doc_code_desc: Optional[str] = None
    doc_group_code: Optional[str] = None
    shareable: Optional[bool] = None

    def download(self, filename="", path="."):
        return run_sync(self.adownload(filename, path))

    async def adownload(self, filename="", path="."):
        out_path = Path(path).expanduser() / (
            f'{self.date.isoformat()} - {self.doc_desc.replace("/", "_")}.pdf' if not filename else filename
        )
        return await global_dossier_async_api.get_document(
            self.country, self.doc_number, self.doc_id, out_path=out_path
        )


@dataclass
class DocumentList(Model):
    __manager__ = "patent_client.uspto.global_dossier.manager.GlobalDossierDocument"
    title: Optional[str] = None
    doc_number: Optional[str] = None
    country: Optional[str] = None
    message: Optional[str] = None
    applicant_names: "ListCollection[str]" = field(default_factory=ListCollection)
    office_action_count: Optional[int] = None
    docs: "ListCollection[Document]" = field(default_factory=ListCollection)
    office_action_docs: "ListCollection[Document]" = field(default_factory=ListCollection)
