import datetime
from pathlib import Path

import lxml.etree as ET

from .convert import convert_xml_to_json
from .model import Assignment
from .model import AssignmentPage

test_dir = Path(__file__).parent / "fixtures"


def test_assignment_1():
    xml_file = test_dir / "assignment_1.xml"
    input_data = convert_xml_to_json(ET.fromstring(xml_file.read_bytes()))
    page = AssignmentPage.model_validate(input_data)
    a = page.docs[0]
    assert a.id == "18247-405"
    assert a.conveyance_text == "NUNC PRO TUNC ASSIGNMENT"
    assert a.last_update_date <= datetime.date.fromisoformat("2008-01-22")
    assert a.transaction_date.isoformat() == "2019-07-11"
    assert a.recorded_date.isoformat() == "2006-09-14"
    assert a.correspondent.name == "JEFFREY H. INGERMAN"
    assert (
        a.correspondent.address
        == "FISH & NEAVE IP GROUP, ROPES & GRAY LLP\n1251 AVENUE OF THE AMERICAS C3\nNEW YORK, NY 10020-1105"
    )
    assert len(a.assignors) == 1
    assert a.assignors[0].name == "REALTIME DATA COMPRESSION SYSTEMS, INC."
    assert a.assignors[0].execution_date.isoformat() == "2006-09-14"
    assert len(a.assignees) == 1
    assert a.assignees[0].name == "REALTIME DATA LLC"
    assert a.assignees[0].address == "15 WEST 36TH STREET\nNEW YORK, NEW YORK 10018"
    assert len(a.properties) == 5
    assert a.properties[0].invention_title == "SYSTEM AND METHODS FOR ACCELERATED DATA STORAGE AND RETRIEVAL"
    assert a.properties[0].appl_num == "10628795"
    assert a.properties[0].filing_date.isoformat() == "2003-07-28"
    assert a.properties[0].intl_publ_date == None
    assert a.properties[0].intl_reg_num == None
    assert a.properties[0].inventors == "James J. Fallon"
    assert a.properties[0].issue_date.isoformat() == "2006-10-31"
    assert a.properties[0].pat_num == "7130913"
    assert a.properties[0].pct_num == None
    assert a.properties[0].publ_date.isoformat() == "2004-04-15"
    assert a.properties[0].publ_num == "20040073746"


def test_manager():
    a = Assignment.objects.get("18247-405")
    assert a.id == "18247-405"
