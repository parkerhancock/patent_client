import datetime
import re
import typing as tp
from pathlib import Path

from pydantic import BeforeValidator, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from patent_client.util.pydantic_util import BaseModel, DateTime

if tp.TYPE_CHECKING:
    from ..peds.model import USApplication

MDYDate = Annotated[
    datetime.date,
    BeforeValidator(lambda x: datetime.datetime.strptime(x, "%m-%d-%Y").date()),
]


class PtabBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        str_strip_whitespace=True,
    )


class AdditionalRespondent(PtabBaseModel):
    application_number_text: tp.Optional[str] = None
    inventor_name: tp.Optional[str] = None
    patent_number: tp.Optional[str] = None
    party_name: tp.Optional[str] = None


class PtabProceeding(PtabBaseModel):
    """A PTAB Proceeding - e.g. IPR/CBM/DER Trial, Patent Appeal, Interference, etc.

    All fields are query-able. Date ranges can be formed by inserting "from" or "to" on a query
    for a date range.

    """

    # Proceeding Metadata
    last_modified_date: tp.Optional[DateTime] = None
    last_modified_user_id: tp.Optional[DateTime] = None
    institution_decision_date: tp.Optional[MDYDate] = None
    proceeding_filing_date: tp.Optional[MDYDate] = None
    accorded_filing_date: tp.Optional[MDYDate] = None
    proceeding_status_category: tp.Optional[str] = None
    proceeding_number: tp.Optional[str] = None
    proceeding_last_modified_date: tp.Optional[MDYDate] = None
    proceeding_type_category: tp.Optional[str] = None
    subproceeding_type_category: tp.Optional[str] = None
    decision_date: tp.Optional[MDYDate] = None
    docket_notice_mail_date: tp.Optional[MDYDate] = None
    declaration_date: tp.Optional[MDYDate] = None
    style_name_text: tp.Optional[str] = None

    # Respondent Information
    respondent_technology_center_number: tp.Optional[str] = None
    respondent_patent_owner_name: tp.Optional[str] = None
    respondent_party_name: tp.Optional[str] = None
    respondent_group_art_unit_number: tp.Optional[str] = None
    respondent_inventor_name: tp.Optional[str] = None
    respondent_counsel_name: tp.Optional[str] = None
    respondent_grant_date: tp.Optional[MDYDate] = None
    respondent_patent_number: tp.Optional[str] = None
    respondent_application_number_text: tp.Optional[str] = None
    respondent_publication_number: tp.Optional[str] = None
    respondent_publication_date: tp.Optional[MDYDate] = None

    # Petitioner Information
    petitioner_technology_center_number: tp.Optional[str] = None
    petitioner_patent_owner_name: tp.Optional[str] = None
    petitioner_party_name: tp.Optional[str] = None
    petitioner_group_art_unit_number: tp.Optional[str] = None
    petitioner_inventor_name: tp.Optional[str] = None
    petitioner_counsel_name: tp.Optional[str] = None
    petitioner_grant_date: tp.Optional[MDYDate] = None
    petitioner_patent_number: tp.Optional[str] = None
    petitioner_application_number_text: tp.Optional[str] = None

    # Appellant Information
    appellant_technology_center_number: tp.Optional[str] = None
    appellant_patent_owner_name: tp.Optional[str] = None
    appellant_party_name: tp.Optional[str] = None
    appellant_group_art_unit_number: tp.Optional[str] = None
    appellant_inventor_name: tp.Optional[str] = None
    appellant_counsel_name: tp.Optional[str] = None
    appellant_grant_date: tp.Optional[MDYDate] = None
    appellant_patent_number: tp.Optional[str] = None
    appellant_application_number_text: tp.Optional[str] = None
    appellant_publication_date: tp.Optional[MDYDate] = None
    appellant_publication_number: tp.Optional[str] = None
    third_party_name: tp.Optional[str] = None

    # Second Respondent (if any)
    second_respondent_party_name: tp.Optional[str] = None
    second_respondent_appl_number_text: tp.Optional[str] = None
    second_respondent_patent_number: tp.Optional[str] = None
    second_respondent_grant_date: tp.Optional[MDYDate] = None
    second_respondent_patent_owner_name: tp.Optional[str] = None
    second_respondent_inventor_name: tp.Optional[str] = None
    second_respondent_counsel_name: tp.Optional[str] = None
    second_respondent_g_a_u_number: tp.Optional[str] = None
    second_respondent_tech_center_number: tp.Optional[str] = None
    second_respondent_pub_number: tp.Optional[str] = None
    second_respondent_publication_date: tp.Optional[MDYDate] = None

    additional_respondents: tp.List[str] = Field(default_factory=list)

    @property
    def documents(
        self,
    ) -> "list[PtabDocument]":
        """Documents associated with the Proceeding"""
        return self._get_model(".model.PtabDocument").objects.filter(
            proceeding_number=self.proceeding_number
        )

    @property
    def decisions(
        self,
    ) -> "list[PtabDecision]":
        """Decisions associated with the Proceeding"""
        return self._get_model(".model.PtabDecision").objects.filter(
            proceeding_number=self.proceeding_number
        )

    @property
    def us_application(
        self,
    ) -> "list[USApplication]":
        """The US Application provided by PEDS associated with the Proceeding"""
        return self._get_model(".model.USApplication").objects.get(
            patent_number=self.respondent_patent_number
        )


fname_re = re.compile(r"[<>:\"/\|?*]")


class PtabDocument(PtabBaseModel):
    document_identifier: str = Field(repr=False, default=None)
    document_category: tp.Optional[str] = None
    document_type_name: tp.Optional[str] = None
    document_number: tp.Optional[int] = None
    document_name: tp.Optional[str] = None
    document_filing_date: tp.Optional[MDYDate] = None
    proceeding_number: tp.Optional[str] = None
    proceeding_type_category: tp.Optional[str] = Field(repr=False, default=None)
    title: tp.Optional[str] = None

    @property
    def proceeding(self) -> "PtabProceeding":
        """The PTAB proceeding associated with the document"""
        return self._get_model(".model.PtabProceeding").objects.get(
            proceeding_number=self.proceeding_number
        )

    async def download(self, path: tp.Optional[tp.Union[str, Path]]) -> Path:
        from .api import client

        name, ext = self.document_name.rsplit(".", 1)
        name = name[:100] + "." + ext
        filename = f"[{str(self.document_number).rjust(4, '0')}] {self.document_filing_date.isoformat()} - {name}"
        filename = filename.encode(encoding="ascii", errors="ignore").decode("ascii")
        filename = fname_re.sub("", filename)
        out_path = Path(path) if path else Path.cwd()
        if out_path.is_dir():
            out_path = Path(path) / filename
        else:
            out_path = out_path
        download_url = (
            f"https://developer.uspto.gov/ptab-api/documents/{self.document_identifier}/download"
        )
        return await client.download(download_url, path=out_path)


class PtabDecision(PtabBaseModel):
    proceeding_number: str
    board_rulings: tp.List[str] = Field(default_factory=list)
    decision_type_category: tp.Optional[str] = None
    document_identifier: tp.Optional[str] = None
    document_name: tp.Optional[str] = None
    identifier: tp.Optional[str] = None
    subdecision_type_category: tp.Optional[str] = None
    issue_type: tp.List[str] = Field(default_factory=list)
    object_uu_id: tp.Optional[str] = None
    petitioner_technology_center_number: tp.Optional[str] = None

    @property
    def proceeding(self) -> "PtabProceeding":
        """The PTAB proceeding associated with the document"""
        return self._get_model(".model.PtabProceeding").objects.get(
            proceeding_number=self.proceeding_number
        )


class PtabDocumentPage(PtabBaseModel):
    num_found: tp.Optional[int] = Field(alias="recordTotalQuantity")
    docs: tp.List[PtabDocument] = Field(alias="results", default_factory=list)


class PtabProceedingPage(PtabBaseModel):
    num_found: tp.Optional[int] = Field(alias="recordTotalQuantity")
    docs: tp.List[PtabProceeding] = Field(alias="results", default_factory=list)


class PtabDecisionPage(PtabBaseModel):
    num_found: tp.Optional[int] = Field(alias="recordTotalQuantity")
    docs: tp.List[PtabDecision] = Field(alias="results", default_factory=list)
