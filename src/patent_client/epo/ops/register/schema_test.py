from pathlib import Path
import lxml.etree as ET
from .schema import EpoSearchSchema, EpoDocumentSchema
from patent_client.util.json_encoder import JsonEncoder
import json

test_dir = Path(__file__).parent / "test"

def test_search_schema():
    tree = ET.fromstring((test_dir / "search.xml").read_bytes())
    result = EpoSearchSchema().load(tree)
    (test_dir / "search.json").write_text(json.dumps(result, indent=2, cls=JsonEncoder))


def test_biblio_schema():
    tree = ET.fromstring((test_dir / "biblio.xml").read_bytes())
    result = EpoDocumentSchema().load(tree)
    (test_dir / "biblio.json").write_text(json.dumps(result, indent=2, cls=JsonEncoder))
    breakpoint()
    assert False
