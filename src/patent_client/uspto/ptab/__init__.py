import json
from pathlib import Path

base_dir = Path(__file__).parent
schema_path = base_dir / "ptabApiV2.json"
schema_doc = json.loads(schema_path.read_text())

from .model import PtabDecision, PtabDocument, PtabProceeding
