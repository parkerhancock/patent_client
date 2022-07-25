from pathlib import Path
from .schema import PedsPageSchema

test_dir = Path(__file__).parent / "test"

def test_us_app_12721698():
    data = (test_dir / "app_12721698.json").read_text()
    parser = PedsPageSchema()
    result = parser.load(data)
    assert result.num_found == 1
    assert False