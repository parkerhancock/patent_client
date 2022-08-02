import datetime
import importlib
import json
import typing
from collections import OrderedDict
from dataclasses import dataclass
from dataclasses import fields

from .json_encoder import JsonEncoder
from .manager import QuerySet

ManagerType = typing.TypeVar("ManagerType")


class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        klass = super().__new__(cls, name, bases, dct)
        return klass

    @property
    def objects(cls):
        if cls.__manager__ is None:
            return None
        obj_module, obj_class = cls.__manager__.rsplit(".", 1)
        return getattr(importlib.import_module(obj_module), obj_class)()


class ModelABC(object):
    __manager__ = None


@dataclass
class Model(ModelABC, metaclass=ModelMeta):
    __exclude__ = list()
    __default_fields__ = False

    def __init__(self, *args, **kwargs):
        try:
            return super().__init__(*args, **kwargs)
        except TypeError as e:
            raise TypeError(f"{e.args[0]}\nargs:{args}\nkwargs:{kwargs}")

    def as_dict(self):
        """Convert model to a dictionary representation"""
        output = OrderedDict()
        iterator = self

        for k, v in iterator:
            if k in self.__exclude__:
                continue
            elif isinstance(v, Model):
                output[k] = v.as_dict()
            elif isinstance(v, (list, QuerySet)):
                output[k] = [i.as_dict() if isinstance(v, Model) else i for i in v]
            else:
                output[k] = v

        return output

    def fields(self):
        """Return list of fields"""
        return fields(self)

    def __iter__(self):
        for f in sorted(self.fields(), key=lambda x: x.name):
            if hasattr(self, f.name):
                yield (f.name, getattr(self, f.name))

    def to_pandas(self):
        """Convert object to Pandas Series"""
        import pandas as pd

        dictionary = self.as_dict()
        return pd.Series(dictionary)

    def to_json(self, *args, **kwargs):
        return json.dumps(self.as_dict(), *args, cls=JsonEncoder, **kwargs)
