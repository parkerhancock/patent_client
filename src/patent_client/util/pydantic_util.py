import importlib
from typing import Generic
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
        except (ImportError, AttributeError) as e:
            raise UnmanagedModelException(f"Unable to find manager for {cls.__name__}")
