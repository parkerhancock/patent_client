import json
from pathlib import Path

from .schema import OfficeActionCitationPageSchema
from .schema import OfficeActionFulltextPageSchema
from .schema import OfficeActionRejectionPageSchema

fixture_dir = Path(__file__).parent / "fixtures"


def test_rejection_schema():
    input_path = fixture_dir / "rejection_sample_input.json"
    output_path = fixture_dir / "rejection_sample_output.json"
    input_data = json.loads(input_path.read_text())
    output = OfficeActionRejectionPageSchema().load(input_data)
    output_path.write_text(output.to_json(indent=2))
    correct_output_data = json.loads(output_path.read_text())
    output_json = json.loads(output.to_json(indent=2))
    assert output_json == correct_output_data


def test_citation_schema():
    input_path = fixture_dir / "citation_sample_input.json"
    output_path = fixture_dir / "citationsample_output.json"
    input_data = json.loads(input_path.read_text())
    output = OfficeActionCitationPageSchema().load(input_data)
    output_path.write_text(output.to_json(indent=2))
    correct_output_data = json.loads(output_path.read_text())
    output_json = json.loads(output.to_json(indent=2))
    assert output_json == correct_output_data


def test_fulltext_schema():
    input_path = fixture_dir / "fulltext_sample_input.json"
    output_path = fixture_dir / "fulltext_sample_output.json"
    input_data = json.loads(input_path.read_text())
    output = OfficeActionFulltextPageSchema().load(input_data)
    output_path.write_text(output.to_json(indent=2))
    correct_output_data = json.loads(output_path.read_text())
    output_json = json.loads(output.to_json(indent=2))
    assert output_json == correct_output_data
