import datetime
from pathlib import Path

from .schema import AssignmentPageSchema

test_dir = Path(__file__).parent / "test"


def test_assignment_1():
    xml_file = test_dir / "assignment_1.xml"
    parser = AssignmentPageSchema()
    page = parser.load(xml_file.read_text())
    a = page.docs[0]
    assert a.id == "18247-405"
    assert a.conveyance_text == "NUNC PRO TUNC ASSIGNMENT"
    assert a.last_update_date <= datetime.date.fromisoformat("2008-01-22")
    assert a.transaction_date.isoformat() == "2019-07-11"
    assert a.recorded_date.isoformat() == "2006-09-14"
    assert a.corr_name == "JEFFREY H. INGERMAN"
    assert (
        a.corr_address
        == "FISH & NEAVE IP GROUP, ROPES & GRAY LLP\n1251 AVENUE OF THE AMERICAS C3\nNEW YORK, NY 10020-1105"
    )
    assert len(a.assignors) == 1
    assert a.assignors[0].name == "REALTIME DATA COMPRESSION SYSTEMS, INC."
    assert a.assignors[0].ex_date.isoformat() == "2006-09-14"
    assert len(a.assignees) == 1
    assert a.assignees[0].name == "REALTIME DATA LLC"
    assert a.assignees[0].address == "15 WEST 36TH STREET\nNEW YORK, NEW YORK 10018"
    assert len(a.properties) == 5
    assert a.properties[0].invention_title == "SYSTEM AND METHODS FOR ACCELERATED DATA STORAGE AND RETRIEVAL"
    assert a.properties[0].appl_id == "10628795"
    assert a.properties[0].filing_date.isoformat() == "2003-07-28"
    assert a.properties[0].intl_publ_date == None
    assert a.properties[0].intl_reg_num == None
    assert a.properties[0].inventors == "James J. Fallon"
    assert a.properties[0].issue_date.isoformat() == "2006-10-31"
    assert a.properties[0].pat_num == "7130913"
    assert a.properties[0].pct_num == None
    assert a.properties[0].publ_date.isoformat() == "2004-04-15"
    assert a.properties[0].publ_num == "20040073746"


def test_assignment_2():
    xml_file = test_dir / "assignment_2.xml"
    parser = AssignmentPageSchema()
    page = parser.load(xml_file.read_text())
    a = page.docs[0]
    assert len(a.assignors) == 5


def test_assignment_3():
    xml_file = test_dir / "assignment_3.xml"
    parser = AssignmentPageSchema()
    page = parser.load(xml_file.read_text())
    assert page.num_found == 9
    assert len(page.docs) == 9
