import importlib
from itertools import zip_longest
from typing import Generic
from typing import Sequence
from typing import TypeVar

from patent_client.util.base.manager import Manager
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class ClassProperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class UnmanagedModelException(Exception):
    pass


M = TypeVar("M", bound=Manager)


class BaseModel(PydanticBaseModel, Generic[M]):
    model_config = ConfigDict(
        ignored_types=(ClassProperty,),
    )

    @ClassProperty
    def objects(cls) -> M:
        manager_module = cls.__module__.split(".model")[0] + ".manager"
        manager_class_name = cls.__name__ + "Manager"
        try:
            manager_class = getattr(importlib.import_module(manager_module), manager_class_name)
            return manager_class()
        except AttributeError as e:
            raise UnmanagedModelException(
                f"Unable to find manager for {cls.__name__}, looked in {manager_module}.{manager_class_name}"
            )


def zip_fields(values: dict, field_names: Sequence[str]):
    lists = [values.get(key, list()) for key in field_names]
    lists = [v if isinstance(v, list) else list() for v in lists]
    tuples = list(zip_longest(*lists))
    return [dict(zip(field_names, t)) for t in tuples]
