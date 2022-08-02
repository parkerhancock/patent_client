from dataclasses import dataclass
from dataclasses import field
from typing import List

from patent_client.util import Model

from ...util import InpadocModel


@dataclass
class Inpadoc(InpadocModel):
    __manager__ = "patent_client.epo.ops.published.manager.SearchManager"
    family_id: str = None
    id_type: str = None
    country: str = None
    doc_number: str = None
    kind: str = None

    @property
    def docdb_number(self):
        return f"{self.country}{self.doc_number}{self.kind}"

    def download(self, path="."):
        return self.images.full_document.download(path)


@dataclass
class Search(Model):
    query: str = None
    num_results: int = None
    begin: int = None
    end: int = None
    results: List[Inpadoc] = field(default_factory=list)
