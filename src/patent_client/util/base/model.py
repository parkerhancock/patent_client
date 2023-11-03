import importlib
from dataclasses import dataclass
from dataclasses import fields
from typing import TypeVar

from yankee.data.util import DataConversion
from yankee.util import is_valid

ManagerType = TypeVar("ManagerType")


class ClassProperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


@dataclass
class Model(DataConversion):
    @ClassProperty
    def objects(cls) -> ManagerType:
        manager_module = cls.__module__.split(".model")[0] + ".manager"
        manager_class_name = cls.__name__ + "Manager"
        manager_class = getattr(importlib.import_module(manager_module), manager_class_name)
        return manager_class()

    @classmethod
    def fields(cls):
        """Return list of fields"""
        return fields(cls)

    def __iter__(self):
        return self.items()

    def items(self):
        if hasattr(self, "__default_fields__") and self.__default_fields__:
            fields = self.__default_fields__
        else:
            fields = sorted(f.name for f in self.fields())
        excluded_fields = getattr(self, "__exclude_fields__", [])
        for f in fields:
            if f in excluded_fields:
                continue
            value = getattr(self, f, None)
            if is_valid(value):
                yield (f, value)
