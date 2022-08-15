from .api import convert_number


def test_docdb_to_epodoc():
    actual = convert_number("MD.20050130.A.20050130", "application", "docdb", "epodoc")
    assert not actual.messages
    assert actual.input_doc.id_type == "docdb"
    assert actual.output_doc.id_type == "epodoc"


def test_original_to_docdb():
    actual = convert_number("JP.(2006-147056).A.20060526", "application", "original", "docdb")
    assert not actual.messages
    assert actual.input_doc.id_type == "original"
    assert actual.output_doc.id_type == "docdb"


def test_docdb_to_original():
    actual = convert_number("JP.2006147056.A.20060526", "application", "docdb", "original")
    assert not actual.messages
    assert actual.input_doc.id_type == "docdb"
    assert actual.output_doc.id_type == "original"


def test_original_to_epodoc():
    actual = convert_number("US.(08/921,321).A.19970829", "application", "original", "epodoc")
    assert not actual.messages
    assert actual.input_doc.id_type == "original"
    assert actual.output_doc.id_type == "epodoc"


def test_original_to_docdb_pct():
    actual = convert_number("PCT/GB02/04635.20021011", "application", "original", "docdb")
    assert actual.input_doc.id_type == "original"
    assert actual.output_doc.id_type == "docdb"
