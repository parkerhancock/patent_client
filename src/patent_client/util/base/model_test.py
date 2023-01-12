from dataclasses import dataclass

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
    assert type(Example.objects) == DummyManager
