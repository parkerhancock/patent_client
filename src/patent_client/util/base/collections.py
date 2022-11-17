import json
from copy import deepcopy
from itertools import chain

from ..json_encoder import JsonEncoder
from .row import Row
from .util import resolve
from .util import to_dict


class Collection:
    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        return iter(self.iterable)

    # def __len__(self):
    #    return len(self.iterable)

    def len(self):
        return len(self)

    def count(self):
        return len(self)

    def __repr__(self):
        if hasattr(self, "iterable"):
            return f"Collection({repr(self.iterable)})"
        return super().__repr__()

    def __add__(self, other):
        return Collection(chain(self, other))

    def to_list(self):
        """Return a list of item objects from the Manager"""
        return ListManager(self)

    def to_records(self, item_class=None, collection_class=None):
        """Return a list of dictionaries containing item data in ordinary Python types
        Useful for ingesting into NoSQL databases
        """
        item_class = item_class or Row
        collection_class = collection_class or self.__class__
        return to_dict(self, item_class, collection_class)

    def to_json(self, *args, **kwargs) -> str:
        """Convert objects to JSON format"""
        return json.dumps(list(self.to_records()), *args, cls=JsonEncoder, **kwargs)

    def to_pandas(self, annotate=list()):
        """Convert Collection into a Pandas DataFrame"""
        import pandas as pd

        list_of_series = list()
        for i in iter(self):
            try:
                series = i.to_pandas()
            except AttributeError:
                series = pd.Series(i)
            for a in annotate:
                series[a] = resolve(i, a)
            list_of_series.append(series)
        return pd.DataFrame(list_of_series)

    def explode(self, attribute):
        """Implement an "explode" function for nested listed objects."""
        return ExplodedManager(self, attribute)

    def unpack(self, attribute, connector=".", prefix=True):
        """Implement an "unpack" function for nested single objects"""
        return UnpackedManager(self, attribute, connector, prefix)

    # Values
    def values(self, *fields, **kw_fields):
        """Return a Manager that will return a Row object for each item with a subset of attributes
        positional arguments will result in Row objects where the fields match the field names on the item,
        keyword arguments can be used to rename attributes. When passed as key=field, the resulting dictionary will have key: item[field]
        """
        return ValuesManager(self, *fields, **kw_fields)

    def values_list(self, *fields, flat=False, **kw_fields):
        """Return a Manager that will return tuples for each item with a subset of attributes.
        If only a single field is passed, the keyword argument "flat" can be passed to return a simple list"""
        return ValuesListManager(self, *fields, flat=flat, **kw_fields)


class ExplodedManager(Collection):
    def __init__(self, iterable, attribute):
        self.iterable = iterable
        self.attribute = attribute

    def __iter__(self):
        for row in self.iterable:
            explode_field = resolve(row, self.attribute)
            for item in explode_field:
                new_row = row.to_dict()
                new_row[self.attribute] = item
                yield new_row


class UnpackedManager(Collection):
    def __init__(self, iterable, attribute, connector=".", prefix=True):
        self.iterable = iterable
        self.attribute = attribute
        self.connector = connector
        self.prefix = prefix

    def item_key(self, k):
        if not self.prefix:
            return k
        else:
            return f"{self.attribute}{self.connector}{k}"

    def __iter__(self):
        for row in self.iterable:
            unpack_field = {self.item_key(k): v for k, v in resolve(row, self.attribute).items()}
            new_row = Row({**row, **unpack_field})
            del new_row[self.attribute]
            yield new_row


class ListManager(list, Collection):
    def __getitem__(self, sl):
        result = list(self)[sl]
        if isinstance(sl, slice):
            return ListManager(result)
        else:
            return result


class ValuesManager(Collection):
    def __init__(self, manager, *arg_fields, fields=dict(), **kw_fields):
        self.manager = manager
        self.fields = {**{k: k for k in arg_fields}, **kw_fields, **fields}

    def __iter__(self):
        for item in self.manager:
            yield Row((k, resolve(item, v)) for k, v in self.fields.items())

    def __getitem__(self, sl):
        mger = deepcopy(self)
        new_mgr = mger.manager.__getitem__(sl)
        return new_mgr


class ValuesListManager(ValuesManager):
    def __init__(self, managers, *fields, flat=False, **kw_fields):
        super(ValuesListManager, self).__init__(managers, *fields, **kw_fields)
        self.flat = flat

    def __iter__(self):
        if self.flat and len(self.fields) > 1:
            raise ValueError("Flat only works with 1 field!")
        for row in super(ValuesListManager, self).__iter__():
            data = tuple(row.values())
            yield data[0] if self.flat else data
