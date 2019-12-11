import itertools
from copy import deepcopy
from collections import OrderedDict


class Manager:
    """
    Manager Base Class

    This class is essentially a configurable generator. It is intended to be initialized 
    as an empty object at Model.objects. Users can then modify the manager by calling either:
        
        Manager.filter -> adds filter criteria
        Manager.sort -> adds sorting criteria
        Manager.options -> adds key:value options

    All methods should return a brand-new manager with the appropriate parameters re-set. The 
    Manager also has a special method to fetch a single matching object:

        Manager.get -> adds filter critera, and returns the first object if only one object is found, else raises an Exception

    The manager's attributes are stored in a dictionary at Manager.config. Config has the following structure:

        {
            'filter': {
                key: value,
                key: value,
            },
            'order_by': [value, value, value],
            'values': [value, value, value]
            'options': {
                key: value
            }
        }
        
    """

    primary_key = None

    def __init__(
        self,
        config=dict(
            filter=dict(), order_by=list(), options=dict(), limit=None, offset=0
        ),
    ):
        self.config = config

    def __add__(self, other):
        return QuerySet((self, other))

    def __eq__(self, other):
        return self.config == other.config

    def __getitem__(self, key):
        print(key)
        if isinstance(key, slice):
            if key.step != None:
                raise AttributeError("Step is not supported")
            mger = self.offset(key.start + self.config["offset"])
            mger = mger.limit(key.stop - key.start)
            return mger
        return self.offset(key).first()

    def filter(self, *args, **kwargs):
        if args:
            kwargs[self.primary_key] = args
        for k, v in kwargs.items():
            if not isinstance(v, str):
                try:
                    kwargs[k] = list(str(i) for i in v)
                except TypeError:
                    kwargs[k] = str(v)
            else:
                kwargs[k] = [v]
        new_config = deepcopy(self.config)
        new_config["filter"] = {**new_config["filter"], **kwargs}
        return self.__class__(new_config)

    def order_by(self, *args):
        """Take arguments, and store in a special keyword argument called 'sort' """
        new_config = deepcopy(self.config)
        new_config["order_by"] = list(new_config["order_by"]) + list(args)
        return self.__class__(new_config)

    def set_options(self, **kwargs):
        new_config = deepcopy(self.config)
        new_config["options"] = {**new_config["options"], **kwargs}
        return self.__class__(new_config)

    def limit(self, limit):
        new_config = deepcopy(self.config)
        new_config["limit"] = limit
        return self.__class__(new_config)

    def offset(self, offset):
        new_config = deepcopy(self.config)
        new_config["offset"] += offset
        return self.__class__(new_config)

    def get(self, *args, **kwargs):
        """Implement a new manager with the requested keywords, and if the length is 1,
        return that record, else raise an exception"""
        manager = self.filter(*args, **kwargs)
        if len(manager) > 1:
            raise ValueError("More than one document found!")
        return manager[0]

    # Manager Functions

    def count(self):
        return len(self)

    def first(self):
        return next(iter(self))

    def all(self):
        return self

    def to_pandas(self, limit=50):
        import pandas as pd

        objects = list(self)
        return pd.DataFrame.from_records(OrderedDict(r) for r in objects)

    def explode(self, attribute):
        from itertools import chain

        return QuerySet(chain.from_iterable(getattr(r, attribute, None) for r in self))

    # Values
    def values(self, *fields):
        return ValuesQuerySet([self], fields)

    def values_list(self, *fields, flat=False):
        return ValuesListQuerySet([self], fields, flat)


class QuerySet(Manager):
    """
    Utility class that extends the Manager helper function to 
    any collection of Patent Client objects
    """

    def __init__(self, iterables):
        self.iterables = iterables

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [
                self[k]
                for k in range(key.start or 0, key.stop or len(self), key.step or 1)
            ]
        else:
            offset = 0
            for iterable in self.iterables:
                if offset + len(iterable) > key:
                    return iterable[key - offset]

    def __iter__(self):
        for item in itertools.chain(*self.iterables):
            yield item

    def __len__(self):
        return sum(len(i) for i in self.iterables)

    def __repr__(self):
        return f"<QuerySet({self.iterables})>"


def resolve(item, key):
    accessors = key.split(".")
    try:
        for accessor in accessors:
            if accessor.isdigit():
                item = item[int(accessor)]
            elif isinstance(item, dict):
                item = item[accessor]
            else:
                item = getattr(item, accessor)
    except Exception as e:
        e.args = (e.__class__, *e.args)
        return e
    return item


class ValuesQuerySet(QuerySet):
    def __init__(self, iterables, fields):
        super(ValuesQuerySet, self).__init__(iterables)
        self.fields = fields

    def __iter__(self):
        for iterable in self.iterables:
            for item in iterable:
                yield OrderedDict((f, resolve(item, f)) for f in self.fields)


class ValuesListQuerySet(ValuesQuerySet):
    def __init__(self, iterable, fields, flat=False):
        super(ValuesListQuerySet, self).__init__(iterable, fields)
        self.flat = flat

    def __iter__(self):
        if self.flat and len(self.fields) > 1:
            raise ValueError("Flat only works with 1 field!")
        for data_dict in super(ValuesListQuerySet, self).__iter__():
            data = tuple(data_dict.values())
            yield data[0] if self.flat else data
