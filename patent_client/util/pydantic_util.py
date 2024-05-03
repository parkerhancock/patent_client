import datetime
import importlib
import re
import typing as tp

from async_property.base import AsyncPropertyDescriptor
from dateutil.parser import isoparse
from dateutil.parser import parse as parse_dt
from pydantic import BaseModel as PydanticBaseModel
from pydantic import BeforeValidator, ConfigDict
from typing_extensions import Annotated

from patent_client.util.manager import Manager


def parse_datetime(date_obj: tp.Union[str, datetime.datetime]) -> datetime.datetime:
    if isinstance(date_obj, datetime.datetime):
        return date_obj
    try:
        return isoparse(date_obj)
    except ValueError:
        return parse_dt(date_obj)


def parse_date(
    date_obj: tp.Union[str, datetime.datetime, datetime.date],
) -> datetime.date:
    if isinstance(date_obj, datetime.date):
        return date_obj
    elif isinstance(date_obj, datetime.datetime):
        return date_obj.date()
    try:
        return isoparse(date_obj).date()
    except ValueError:
        return parse_dt(date_obj).date()


DateTime = Annotated[datetime.datetime, BeforeValidator(parse_datetime)]
Date = Annotated[datetime.date, BeforeValidator(parse_date)]


class ClassProperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class UnmanagedModelException(Exception):
    pass


M = tp.TypeVar("M", bound=Manager)


leading_period_re = re.compile(r"^\.+")


def get_class(class_name: str, base_class: type) -> type:
    if class_name.startswith("."):
        base_module = base_class.__module__
        # Count the number of dots to determine how many levels to go up
        level_up = leading_period_re.match(class_name).span()[1]
        module_path = base_module.split(".")[:-level_up]
        absolute_model_name = ".".join(module_path) + "." + class_name[level_up:]
    else:
        absolute_model_name = class_name

    module_name, class_name = absolute_model_name.rsplit(".", 1)
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import {absolute_model_name}: {e}")


class BaseModel(PydanticBaseModel, tp.Generic[M]):
    __manager__: tp.Optional[str] = None
    model_config = ConfigDict(
        ignored_types=(ClassProperty, AsyncPropertyDescriptor),
    )

    @ClassProperty
    def objects(cls) -> M:
        if cls.__manager__ is not None:
            manager_path = cls.__manager__
        else:
            manager_module = cls.__module__.split(".model")[0] + ".manager"
            manager_path = manager_module + "." + cls.__name__ + "Manager"
        return get_class(manager_path, base_class=cls)()

    def to_dict(self):
        return self.model_dump()

    def items(self):
        return iter(self)

    def _get_model(self, model_name: str, base_class=None) -> tp.Type["BaseModel"]:
        base_class = self.__class__ if base_class is None else base_class
        return get_class(model_name, base_class)
