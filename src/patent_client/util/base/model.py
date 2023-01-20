import importlib
import typing
from dataclasses import dataclass
from dataclasses import fields

from yankee.data.util import DataConversion
from yankee.util import is_valid

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
class Model(ModelABC, DataConversion, metaclass=ModelMeta):
    __exclude_fields__ = list()
    __default_fields__ = False

    # def __init__(self, *args, **kwargs):
    #    try:
    #        return super().__init__(*args, **kwargs)
    #    except TypeError as e:
    #        raise TypeError(f"{e.args[0]}\nargs:{args}\nkwargs:{kwargs}")

    def fields(self):
        """Return list of fields"""
        return fields(self)

    def __iter__(self):
        return self.items()

    def items(self):
        if self.__default_fields__:
            fields = self.__default_fields__
        else:
            fields = sorted(f.name for f in self.fields())
        for f in fields:
            if f in self.__exclude_fields__:
                continue
            value = getattr(self, f, None)
            if is_valid(value):
                yield (f, value)
