from dataclasses import dataclass

import pandas as pd
import pytest

from .model import Model


def test_model():
    class DummyManager:
        pass

    @dataclass
    class Example(Model):
        __manager__ = DummyManager
        a: str = None
        b: int = None

    ex = Example(a="1", b=2)
    assert len(ex.fields()) == 2
    assert ex.a == "1"
    assert ex.b == 2
    d = ex.to_dict(item_class=dict)
    assert type(d) == dict
    with pytest.raises(AttributeError):
        assert d.a == "1"
    assert d == {"a": "1", "b": 2}
    s = ex.to_pandas()
    assert type(s) == pd.Series
    assert s.a == "1"
    assert s.b == 2
    assert s.to_json() == '{"a":"1","b":2}'
    assert type(Example.objects) == DummyManager


def test_exclude_fields():
    @dataclass
    class Example(Model):
        __exclude_fields__ = [
            "b",
        ]
        a: str = None
        b: int = None

    ex = Example(a="1", b=2)
    row = ex.to_dict()
    assert "b" not in row
