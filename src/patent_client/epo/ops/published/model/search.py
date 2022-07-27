from dataclasses import dataclass, field

from patent_client.util import Model

@dataclass
class SearchResult(Model):
    family_id: str = None
    id_type: str = None
    country: str = None
    doc_number: str = None
    kind: str = None

@dataclass
class Search(Model):
    query: str = None
    num_results: int = None
    begin: int = None
    end: int = None
    results: list = field(default_factory=list)