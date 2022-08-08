from yankee.util import AttrDict
from .test import autogen_tests


def test_autogen_tests():
    d = {
        "a": 1,
        "b": "name", 
        "c": [5, 6, 7], 
        "d": {"fname": "Parker", "lname": "Hancock"},
        "e": [
            {"x": 1, "y": 2, "z": 3},
            {"x": 4, "y": 5, "z": 6},
            {"x": 7, "y": 8, "z": 9},
        ],
    }
    d = AttrDict.convert(d)
    result = autogen_tests("d", d)
    assert result == """assert d.a == 1
assert d.b == name
assert d.c[0] == 5
assert d.d.fname == Parker
assert d.d.lname == Hancock
assert d.e[2].x == 7
assert d.e[2].y == 8
assert d.e[2].z == 9"""