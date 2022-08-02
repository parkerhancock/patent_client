from __future__ import annotations

import datetime
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from patent_client import session
from patent_client.util import Model
from patent_client.util import one_to_many
from patent_client.util import one_to_one

from patent_client.util.claims.parser import ClaimsParser


@dataclass
class Inventor(Model):
    city: str = None
    first_name: str = None
    last_name: str = None
    region: str = None


@dataclass
class Applicant(Model):
    city: str = None
    country: str = None
    name: str = None
    state: str = None
    type: str = None


@dataclass
class Assignee(Model):
    city: str = None
    name: str = None
    region: str = None

@dataclass
class Examiner(Model):
    first_name: str = None
    last_name: str = None

@dataclass
class RelatedPatentDocument(Model):
    appl_id: str
    filing_date: datetime.date = None
    patent_number: str = None


@dataclass
class PriorPublication(Model):
    publication_number: str
    publication_date: datetime.date


@dataclass
class USReference(Model):
    date: str
    first_named_inventor: str
    publication_number: str


@dataclass
class ForeignReference(Model):
    publication_number: str
    date: str
    country_code: str


@dataclass
class NPLReference(Model):
    citation: str


@dataclass
class CpcClass(Model):
    classification: str
    version: str


@dataclass
class USClass(Model):
    classification: str
    subclassification: str


@dataclass
class ForeignPriority(Model):
    date: datetime.date
    country_code: str
    number: str


@dataclass
class Publication(Model):
    __manager__ = "patent_client.uspto.fulltext.base.manager.FullTextManager"
    publication_number: str
    kind_code: str
    publication_date: str
    title: str = None
    
    description: str = None
    abstract: str = None
    claims: str = None

    appl_id: str = None
    filing_date: datetime.date = None
    family_id: str = None
    app_early_pub_number: str = None
    app_early_pub_date: datetime.date = None

    parent_case_text: str = None
    pct_filing_date: datetime.date = None
    pct_number: str = None
    national_stage_entry_date: datetime.date = None
    foreign_priority: "List[ForeignPriority]" = field(default_factory=list)

    inventors: list = field(default_factory=list)
    applicants: list = field(default_factory=list)
    assignees: list = field(default_factory=list)
    primary_examiner: str = None
    assistant_examiner: str = None
    agent: str = None
    pdf_url: str = None

    related_us_applications: "List[RelatedPatentDocument]" = field(default_factory=list)
    prior_publications: "List[PriorPublication]" = field(default_factory=list)

    cpc_classes: "List[CpcClass]" = field(default_factory=list)
    intl_classes: "List[CpcClass]" = field(default_factory=list)
    us_classes: "List[USClass]" = field(default_factory=list)
    field_of_search: "List[USClass]" = field(default_factory=list)

    us_references: "List[USReference]" = field(default_factory=list)
    foreign_references: "List[ForeignReference]" = field(default_factory=list)
    npl_references: "List[NPLReference]" = field(default_factory=list)

    def __repr__(self):
        return f"{self.__class__.__name__}(publication_number={self.publication_number}, publication_date={self.publication_date.isoformat()}, title={self.title})"

    @property
    def parsed_claims(self):
        return ClaimsParser().parse(self.claims)

    application = one_to_one(
        "patent_client.uspto.peds.model.USApplication", appl_id="appl_id"
    )


@dataclass
class PublicationResult(Model):
    publication_number: str
    title: str
    publication = one_to_one(
        "patent_client.uspto.fulltext.base.model.Publication",
        publication_number="publication_number",
    )


@dataclass
class Image(Model):
    publication_number: str
    pdf_url: str
    sections: list

    def download(self, path=None):
        response = session.get(self.pdf_url, stream=True)
        response.raise_for_status()
        if path is None:
            path = Path(f"{self.publication_number}.pdf")
        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return path
