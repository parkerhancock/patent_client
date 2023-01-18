import json
from pathlib import Path

__api_name__ = "PTAB API v2"
base_dir = Path(__file__).parent
schema_path = base_dir / "ptabApiV2.json"
schema_doc = json.loads(schema_path.read_text())

from .session import PtabSession

session = PtabSession()
from .model import PtabDecision, PtabDocument, PtabProceeding  # noqa: F401,E402
