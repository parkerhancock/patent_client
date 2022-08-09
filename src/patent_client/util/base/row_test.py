from dataclasses import dataclass

import pandas as pd

from .model import Model
from .row import Row


def test_row():
    row = Row((("first_name", "John"), ("age", 25)))
    # Test length
    assert len(row) == 2
    # Test attribute access
    assert row.first_name == "John"
    assert row.age == 25
    # Test data conversion
    assert row.to_dict() == row
    s = row.to_pandas()
    assert type(s) == pd.Series
    assert s.first_name == "John"
    assert row.age == 25
    j = row.to_json()
    assert j == '{"first_name": "John", "age": 25}'


def test_row_from_dataclass():
    @dataclass
    class TestData(Model):
        a: int = None
        b: int = None

    dc = TestData(a=1, b=2)
    row = Row(dc)
    assert row.a == 1
    assert row.b == 2
