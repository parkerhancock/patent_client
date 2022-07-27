from patent_client.util.test import compare_dicts
import json

from pathlib import Path
from .schema import PedsPageSchema

test_dir = Path(__file__).parent / "test"

def test_us_app_12721698():
    data = (test_dir / "app_12721698.json").read_text()
    parser = PedsPageSchema()
    result = json.loads(parser.load(data).to_json())
    expected = json.loads((test_dir / "expected.json").read_text())
    compare_dicts(expected, result)