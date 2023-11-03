from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional

from patent_client.util import Model

from ...util import InpadocModel


@dataclass
class Inpadoc(InpadocModel):
    family_id: Optional[str] = None
    id_type: Optional[str] = None
    country: Optional[str] = None
    doc_number: Optional[str] = None
    kind: Optional[str] = None

    @property
    def docdb_number(self):
        return f"{self.country}{self.doc_number}{self.kind}"

    def download(self, path="."):
        return self.images.full_document.download(path)


@dataclass
class Search(Model):
    query: Optional[str] = None
    num_results: Optional[int] = None
    begin: Optional[int] = None
    end: Optional[int] = None
    results: List[Inpadoc] = field(default_factory=list)
