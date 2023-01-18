from pathlib import Path

from .api import FamilyApi

test_dir = Path(__file__).parent / "fixtures" / "examples"
expected_dir = Path(__file__).parent / "fixtures" / "expected"


def test_example():
    result = FamilyApi.get_family("EP1000000A1")
    expected_file = expected_dir / "example.xml"
    # expected_file.write_text(result)
    expected = expected_file.read_text()
    assert expected == result
