from .manager import TessManager


def test_get_length():
    assert TessManager().filter(query="Nike[FM]").count() == 55

def test_limit():
    assert TessManager().filter(query="Nike[FM]").limit(50).count() == 50

def test_offset():
    assert TessManager().filter(query="Nike[FM]").offset(15).count() == 40