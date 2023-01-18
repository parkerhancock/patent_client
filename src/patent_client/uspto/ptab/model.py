import datetime
import re
from dataclasses import dataclass
from dataclasses import field
from fileinput import filename
from pathlib import Path
from typing import *

from patent_client import session
from patent_client.util import Model
from yankee.data import ListCollection

from ...util.base.related import get_model


@dataclass
class AdditionalRespondent(Model):
    application_number_text: str = None
    inventor_name: str = None
    patent_number: str = None
    party_name: str = None


@dataclass
class PtabProceeding(Model):
    """A PTAB Proceeding - e.g. IPR/CBM/DER Trial, Patent Appeal, Interference, etc.

    All fields are query-able. Date ranges can be formed by inserting "from" or "to" on a query
    for a date range.

    """

    __manager__ = "patent_client.uspto.ptab.manager.PtabProceedingManager"
    # Proceeding Metadata
    last_modified_date: "datetime.datetime" = None
    last_modified_user_id: "datetime.datetime" = None
    institution_decision_date: "datetime.date" = None
    proceeding_filing_date: "datetime.date" = None
    accorded_filing_date: "datetime.date" = None
    proceeding_status_category: str = None
    proceeding_number: str = None
    proceeding_last_modified_date: "datetime.date" = None
    proceeding_type_category: str = None
    subproceeding_type_category: str = None
    decision_date: "datetime.date" = None
    docket_notice_mail_date: "datetime.date" = None
    declaration_date: "datetime.date" = None
    style_name_text: str = None

    # Respondent Information
    respondent_technology_center_number: str = None
    respondent_patent_owner_name: str = None
    respondent_party_name: str = None
    respondent_group_art_unit_number: str = None
    respondent_inventor_name: str = None
    respondent_counsel_name: str = None
    respondent_grant_date: "datetime.date" = None
    respondent_patent_number: str = None
    respondent_application_number_text: str = None
    respondent_publication_number: str = None
    respondent_publication_date: "datetime.date" = None

    # Petitioner Information
    petitioner_technology_center_number: str = None
    petitioner_patent_owner_name: str = None
    petitioner_party_name: str = None
    petitioner_group_art_unit_number: str = None
    petitioner_inventor_name: str = None
    petitioner_counsel_name: str = None
    petitioner_grant_date: "datetime.date" = None
    petitioner_patent_number: str = None
    petitioner_application_number_text: str = None

    # Appellant Information
    appellant_technology_center_number: str = None
    appellant_patent_owner_name: str = None
    appellant_party_name: str = None
    appellant_group_art_unit_number: str = None
    appellant_inventor_name: str = None
    appellant_counsel_name: str = None
    appellant_grant_date: "datetime.date" = None
    appellant_patent_number: str = None
    appellant_application_number_text: str = None
    appellant_publication_date: "datetime.date" = None
    appellant_publication_number: str = None
    third_party_name: str = None

    # Second Respondent (if any)
    second_respondent_party_name: str = None
    second_respondent_appl_number_text: str = None
    second_respondent_patent_number: str = None
    second_respondent_grant_date: "datetime.date" = None
    second_respondent_patent_owner_name: str = None
    second_respondent_inventor_name: str = None
    second_respondent_counsel_name: str = None
    second_respondent_g_a_u_number: str = None
    second_respondent_tech_center_number: str = None
    second_respondent_pub_number: str = None
    second_respondent_publication_date: "datetime.date" = None

    additional_respondents: "ListCollection[str]" = field(default_factory=list)

    def __repr__(self):
        return f"PtabProceeding(subproceeding_type_category='{self.subproceeding_type_category}', proceeding_number='{self.proceeding_number}', proceeding_status_category='{self.proceeding_status_category}', proceeding_type_category='{self.proceeding_type_category}', respondent_party_name='{self.respondent_party_name}')"

    @property
    def documents(self) -> "ListCollection[patent_client.uspto.ptab.model.PtabDocument]":
        """Documents associated with the Proceeding"""
        return get_model("patent_client.uspto.ptab.model.PtabDocument").objects.filter(
            proceeding_number=self.proceeding_number
        )

    @property
    def decisions(self) -> "ListCollection[patent_client.uspto.ptab.model.PtabDecision]":
        """Decisions associated with the Proceeding"""
        return get_model("patent_client.uspto.ptab.model.PtabDecision").objects.filter(
            proceeding_number=self.proceeding_number
        )

    @property
    def us_application(self) -> "ListCollection[patent_client.uspto.peds.model.USApplication]":
        """The US Application provided by PEDS associated with the Proceeding"""
        return get_model("patent_client.uspto.peds.model.USApplication").objects.get(
            patent_number=self.respondent_patent_number
        )


fname_re = re.compile(r"[<>:\"/\|?*]")


@dataclass
class PtabDocument(Model):
    __manager__ = "patent_client.uspto.ptab.manager.PtabDocumentManager"
    document_identifier: str = field(repr=False)
    document_category: str
    document_type_name: str
    document_number: int
    document_name: str
    document_filing_date: datetime.date
    proceeding_number: str = field(repr=False)
    proceeding_type_category: str = field(repr=False)
    title: "Optional[str]" = None

    @property
    def proceeding(self) -> "patent_client.uspto.ptab.model.PtabProceeding":
        """The PTAB proceeding associated with the document"""
        return get_model("patent_client.uspto.ptab.model.PtabProceeding").objects.get(
            proceeding_number=self.proceeding_number
        )

    def download(self, path="."):
        name, ext = self.document_name.rsplit(".", 1)
        name = name[:100] + "." + ext
        filename = f"[{str(self.document_number).rjust(4, '0')}] {self.document_filing_date.isoformat()} - {name}"
        filename = filename.encode(encoding="ascii", errors="ignore").decode("ascii")
        filename = fname_re.sub("", filename)
        out_path = Path(path) / filename
        with session.get(
            f"https://developer.uspto.gov/ptab-api/documents/{self.document_identifier}/download", verify=False
        ) as r:
            r.raise_for_status()
            with out_path.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)


@dataclass
class PtabDecision(Model):
    __manager__ = "patent_client.uspto.ptab.manager.PtabDecisionManager"
    proceeding_number: str
    board_rulings: "List[str]" = field(default_factory=ListCollection)
    decision_type_category: str = None
    document_identifier: str = None
    document_name: str = None
    identifier: str = None
    subdecision_type_category: str = None
    issue_type: "Optional[str]" = None
    object_uu_id: "Optional[str]" = None
    petitioner_technology_center_number: "Optional[str]" = None

    @property
    def proceeding(self) -> "patent_client.uspto.ptab.model.PtabProceeding":
        """The PTAB proceeding associated with the document"""
        return get_model("patent_client.uspto.ptab.model.PtabProceeding").objects.get(
            proceeding_number=self.proceeding_number
        )
