import importlib
from typing import Generic
from typing import Optional
from typing import TypeVar

from patent_client.util.manager import Manager
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
    __manager__: Optional[str] = None
    model_config = ConfigDict(
        ignored_types=(ClassProperty,),
    )

    @ClassProperty
    def objects(cls) -> M:
        if cls.__manager__ is not None:
            manager_module, manager_class_name = cls.__manager__.rsplit(".", 1)
            try:
                manager_class = getattr(importlib.import_module(manager_module), manager_class_name)
                return manager_class()
            except AttributeError as e:
                raise ValueError(
                    f"Specified manager at {cls.__manager__} not found! looked in {manager_module}.{manager_class_name}"
                )
        else:
            manager_module = cls.__module__.split(".model")[0] + ".manager"
            manager_class_name = cls.__name__ + "Manager"
        try:
            manager_class = getattr(importlib.import_module(manager_module), manager_class_name)
            return manager_class()
        except AttributeError as e:
            raise UnmanagedModelException(
                f"Unable to find manager for {cls.__name__}, looked in {manager_module}.{manager_class_name}"
            )

    def to_dict(self):
        return self.model_dump()

    def items(self):
        return iter(self)
