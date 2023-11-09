import datetime
import re
from pathlib import Path
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from patent_client.util.asyncio_util import run_sync
from patent_client.util.pydantic_util import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic import Field
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from ...util.base.related import get_model
from .session import session

if TYPE_CHECKING:
    from patent_client.uspto.peds.model import USApplication

MDYDate = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.strptime(x, "%m-%d-%Y").date())]


class PtabBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        anystr_strip_whitespace=True,
    )


class AdditionalRespondent(PtabBaseModel):
    application_number_text: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_number: Optional[str] = None
    party_name: Optional[str] = None


class PtabProceeding(PtabBaseModel):
    """A PTAB Proceeding - e.g. IPR/CBM/DER Trial, Patent Appeal, Interference, etc.

    All fields are query-able. Date ranges can be formed by inserting "from" or "to" on a query
    for a date range.

    """

    # Proceeding Metadata
    last_modified_date: Optional[datetime.datetime] = None
    last_modified_user_id: Optional[datetime.datetime] = None
    institution_decision_date: Optional[MDYDate] = None
    proceeding_filing_date: Optional[MDYDate] = None
    accorded_filing_date: Optional[MDYDate] = None
    proceeding_status_category: Optional[str] = None
    proceeding_number: Optional[str] = None
    proceeding_last_modified_date: Optional[MDYDate] = None
    proceeding_type_category: Optional[str] = None
    subproceeding_type_category: Optional[str] = None
    decision_date: Optional[MDYDate] = None
    docket_notice_mail_date: Optional[MDYDate] = None
    declaration_date: Optional[MDYDate] = None
    style_name_text: Optional[str] = None

    # Respondent Information
    respondent_technology_center_number: Optional[str] = None
    respondent_patent_owner_name: Optional[str] = None
    respondent_party_name: Optional[str] = None
    respondent_group_art_unit_number: Optional[str] = None
    respondent_inventor_name: Optional[str] = None
    respondent_counsel_name: Optional[str] = None
    respondent_grant_date: Optional[MDYDate] = None
    respondent_patent_number: Optional[str] = None
    respondent_application_number_text: Optional[str] = None
    respondent_publication_number: Optional[str] = None
    respondent_publication_date: Optional[MDYDate] = None

    # Petitioner Information
    petitioner_technology_center_number: Optional[str] = None
    petitioner_patent_owner_name: Optional[str] = None
    petitioner_party_name: Optional[str] = None
    petitioner_group_art_unit_number: Optional[str] = None
    petitioner_inventor_name: Optional[str] = None
    petitioner_counsel_name: Optional[str] = None
    petitioner_grant_date: Optional[MDYDate] = None
    petitioner_patent_number: Optional[str] = None
    petitioner_application_number_text: Optional[str] = None

    # Appellant Information
    appellant_technology_center_number: Optional[str] = None
    appellant_patent_owner_name: Optional[str] = None
    appellant_party_name: Optional[str] = None
    appellant_group_art_unit_number: Optional[str] = None
    appellant_inventor_name: Optional[str] = None
    appellant_counsel_name: Optional[str] = None
    appellant_grant_date: Optional[MDYDate] = None
    appellant_patent_number: Optional[str] = None
    appellant_application_number_text: Optional[str] = None
    appellant_publication_date: Optional[MDYDate] = None
    appellant_publication_number: Optional[str] = None
    third_party_name: Optional[str] = None

    # Second Respondent (if any)
    second_respondent_party_name: Optional[str] = None
    second_respondent_appl_number_text: Optional[str] = None
    second_respondent_patent_number: Optional[str] = None
    second_respondent_grant_date: Optional[MDYDate] = None
    second_respondent_patent_owner_name: Optional[str] = None
    second_respondent_inventor_name: Optional[str] = None
    second_respondent_counsel_name: Optional[str] = None
    second_respondent_g_a_u_number: Optional[str] = None
    second_respondent_tech_center_number: Optional[str] = None
    second_respondent_pub_number: Optional[str] = None
    second_respondent_publication_date: Optional[MDYDate] = None

    additional_respondents: List[str] = Field(default_factory=list)

    @property
    def documents(
        self,
    ) -> "list[PtabDocument]":
        """Documents associated with the Proceeding"""
        return get_model("patent_client.uspto.ptab.model.PtabDocument").objects.filter(
            proceeding_number=self.proceeding_number
        )

    @property
    def decisions(
        self,
    ) -> "list[PtabDecision]":
        """Decisions associated with the Proceeding"""
        return get_model("patent_client.uspto.ptab.model.PtabDecision").objects.filter(
            proceeding_number=self.proceeding_number
        )

    @property
    def us_application(
        self,
    ) -> "list[USApplication]":
        """The US Application provided by PEDS associated with the Proceeding"""
        return get_model("patent_client.uspto.peds.model.USApplication").objects.get(
            patent_number=self.respondent_patent_number
        )


fname_re = re.compile(r"[<>:\"/\|?*]")


class PtabDocument(PtabBaseModel):
    document_identifier: str = Field(repr=False, default=None)
    document_category: Optional[str] = None
    document_type_name: Optional[str] = None
    document_number: Optional[int] = None
    document_name: Optional[str] = None
    document_filing_date: Optional[MDYDate] = None
    proceeding_number: Optional[str] = None
    proceeding_type_category: Optional[str] = Field(repr=False, default=None)
    title: Optional[str] = None

    @property
    def proceeding(self) -> "PtabProceeding":
        """The PTAB proceeding associated with the document"""
        return get_model("patent_client.uspto.ptab.model.PtabProceeding").objects.get(
            proceeding_number=self.proceeding_number
        )

    def download(self, path: Optional[str | Path]) -> Path:
        return run_sync(self.adownload(path))

    async def adownload(self, path: Optional[str | Path]) -> Path:
        name, ext = self.document_name.rsplit(".", 1)
        name = name[:100] + "." + ext
        filename = f"[{str(self.document_number).rjust(4, '0')}] {self.document_filing_date.isoformat()} - {name}"
        filename = filename.encode(encoding="ascii", errors="ignore").decode("ascii")
        filename = fname_re.sub("", filename)
        out_path = Path(path)
        if out_path.is_dir():
            out_path = Path(path) / filename
        else:
            out_path = out_path
        donwload_url = f"https://developer.uspto.gov/ptab-api/documents/{self.document_identifier}/download"
        return await session.download(download_url, path=out_path)


class PtabDecision(PtabBaseModel):
    __manager__ = "patent_client.uspto.ptab.manager.PtabDecisionManager"
    proceeding_number: str
    board_rulings: List[str] = Field(default_factory=list)
    decision_type_category: Optional[str] = None
    document_identifier: Optional[str] = None
    document_name: Optional[str] = None
    identifier: Optional[str] = None
    subdecision_type_category: Optional[str] = None
    issue_type: List[str] = Field(default_factory=list)
    object_uu_id: Optional[str] = None
    petitioner_technology_center_number: Optional[str] = None

    @property
    def proceeding(self) -> "PtabProceeding":
        """The PTAB proceeding associated with the document"""
        return get_model("patent_client.uspto.ptab.model.PtabProceeding").objects.get(
            proceeding_number=self.proceeding_number
        )


class PtabDocumentPage(PtabBaseModel):
    num_found: Optional[int] = Field(alias="recordTotalQuantity")
    docs: List[PtabDocument] = Field(alias="results", default_factory=list)


class PtabProceedingPage(PtabBaseModel):
    num_found: Optional[int] = Field(alias="recordTotalQuantity")
    docs: List[PtabProceeding] = Field(alias="results", default_factory=list)


class PtabDecisionPage(PtabBaseModel):
    num_found: Optional[int] = Field(alias="recordTotalQuantity")
    docs: List[PtabDecision] = Field(alias="results", default_factory=list)
