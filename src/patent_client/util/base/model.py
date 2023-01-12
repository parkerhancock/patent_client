import importlib
import typing
from dataclasses import dataclass


from yankee.data.row import Row

ManagerType = typing.TypeVar("ManagerType")


class ModelMeta(type):
    """Metaclass for automatically appending the .objects attriburte to Model
    classes"""

    def __new__(cls, name, bases, dct):
        klass = super().__new__(cls, name, bases, dct)
        return klass

    @property
    def objects(cls):
        if cls.__manager__ is None:
            return None
        if not isinstance(cls.__manager__, str):
            return cls.__manager__()
        obj_module, obj_class = cls.__manager__.rsplit(".", 1)
        return getattr(importlib.import_module(obj_module), obj_class)()


class ModelABC(object):
    __manager__ = None

@dataclass
class Model(ModelABC, Row, metaclass=ModelMeta):
    pass
