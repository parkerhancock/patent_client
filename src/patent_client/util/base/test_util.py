from .util import resolve


def test_resolve():
    data = {"stuff": [
        {"a": 1},
        {"a": 2},
        {"a": 3},
    ]
    }
    result = resolve(data, "stuff.a")
    assert False