import json
from pathlib import Path

from patent_client.util.test import compare_dicts

from .schema import PedsPageSchema

test_dir = Path(__file__).parent / "test"


def test_us_app_12721698():
    data = (test_dir / "app_12721698.json").read_text()
    parser = PedsPageSchema()
    result = parser.load(data)
    expected_file = test_dir / "expected.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(expected, json.loads(result.to_json()))
