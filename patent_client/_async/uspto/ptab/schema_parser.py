import json
import typing as tp
from pathlib import Path


def extract_allowed_fields(schema_path: Path) -> tp.Dict[str, tp.Set[str]]:
    with open(schema_path, "r") as f:
        schema = json.load(f)

    allowed_fields = {"proceedings": set(), "documents": set(), "decisions": set()}

    for path, path_item in schema["paths"].items():
        if path in ["/proceedings", "/documents", "/decisions"]:
            endpoint = path.strip("/")
            for method in path_item.values():
                if "parameters" in method:
                    for param in method["parameters"]:
                        if param["in"] == "query":
                            allowed_fields[endpoint].add(param["name"])

    return allowed_fields


# Load the schema and extract allowed fields when this module is imported
schema_path = Path(__file__).parent / "docs" / "schema.json"
ALLOWED_FIELDS = extract_allowed_fields(schema_path)
