from typing import List
from dataclasses import dataclass, field

from patent_client.util import Model, one_to_one

@dataclass
class SearchResult(Model):
    __manager__ = "patent_client.epo.ops.published.manager.SearchManager"
    family_id: str = None
    id_type: str = None
    country: str = None
    doc_number: str = None
    kind: str = None

    @property
    def docdb_number(self):
        return f"{self.country}{self.doc_number}{self.kind}"

    biblio = one_to_one("patent_client.epo.ops.published.model.ExchangeDocument", doc_number="docdb_number")
    claims = one_to_one("patent_client.epo.ops.published.model.Claims", attribute="claims", doc_number="docdb_number")
    claim_text = one_to_one("patent_client.epo.ops.published.model.Claims", attribute="claim_text", doc_number="docdb_number")
    description = one_to_one("patent_client.epo.ops.published.model.Description", attribute="description", doc_number="docdb_number")
    family = one_to_one("patent_client.epo.ops.family.model.Family", attribute="family_members", doc_number="docdb_number")
    images = one_to_one("patent_client.epo.ops.published.model.Images", doc_number="docdb_number")

    def download(self, path="."):
        return self.images.full_document.download(path)


@dataclass
class Search(Model):
    query: str = None
    num_results: int = None
    begin: int = None
    end: int = None
    results: List[SearchResult] = field(default_factory=list)