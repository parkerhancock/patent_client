import importlib
import json
from collections import OrderedDict

from ..json_encoder import JsonEncoder
from .util import to_dict


class Row(OrderedDict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __hash__(self):
        return hash(self.to_dict())

    def to_dict(self, item_class=None, collection_class=None):
        item_class = item_class or self.__class__
        collection_class = collection_class or importlib.import_module("patent_client.util.base.collections").Collection
        return to_dict(self, item_class, collection_class)

    def to_pandas(self):
        """Convert object to Pandas Series"""
        import pandas as pd

        return pd.Series(self)

    def to_json(self, *args, **kwargs):
        return json.dumps(self, *args, cls=JsonEncoder, **kwargs)
