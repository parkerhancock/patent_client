import json
from pathlib import Path

import lxml.etree as ET

from .convert import convert_xml_to_json

fixtures = Path(__file__).parent / "fixtures"


def test_assignment_1():
    input_doc = fixtures / "assignment_1.xml"
    output_doc = fixtures / "assignment_1.json"
    output_data = convert_xml_to_json(ET.fromstring(input_doc.read_bytes()))
    # output_doc.write_text(json.dumps(output_data, indent=2))
    expected_data = json.loads(output_doc.read_text())
    assert output_data == expected_data


def test_assignment_2():
    input_doc = fixtures / "assignment_2.xml"
    output_doc = fixtures / "assignment_2.json"
    output_data = convert_xml_to_json(ET.fromstring(input_doc.read_bytes()))
    # output_doc.write_text(json.dumps(output_data, indent=2))
    expected_data = json.loads(output_doc.read_text())
    assert output_data == expected_data


def test_assignment_3():
    input_doc = fixtures / "assignment_3.xml"
    output_doc = fixtures / "assignment_3.json"
    output_data = convert_xml_to_json(ET.fromstring(input_doc.read_bytes()))
    # output_doc.write_text(json.dumps(output_data, indent=2))
    expected_data = json.loads(output_doc.read_text())
    assert output_data == expected_data
