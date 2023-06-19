import dataclasses

from .model import USApplication


def test_fields():
    fields = USApplication.fields()
    for f in fields:
        assert type(f) == dataclasses.Field
