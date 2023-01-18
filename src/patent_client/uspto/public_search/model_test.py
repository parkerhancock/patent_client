from .model import PatentBiblio


def test_simple_lookup():
    app = PatentBiblio.objects.get(patent_number="6103599")
    breakpoint()
    assert False