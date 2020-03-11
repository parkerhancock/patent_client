from __future__ import annotations
import itertools
import importlib
from copy import deepcopy
from collections import OrderedDict
import collections.abc
from typing import Iterable, Iterator, TypeVar, Generic, Union, Sized, List, Any

ModelType = TypeVar('ModelType')

def resolve(item, key):
    if key is None:
        return item
    accessors = key.split(".")
    try:
        for accessor in accessors:
            if accessor.isdigit():
                item = item[int(accessor)]
            elif isinstance(item, dict):
                item = item[accessor]
            else:
                item = getattr(item, accessor)
            if callable(item):
                item = item()
    except Exception as e:
        return None 
    return item

class Manager(Generic[ModelType]):
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
    primary_key: str = ''

    def __init__(
        self,
        config=dict(
            filter=dict(), order_by=list(), options=dict(), limit=None, offset=0, annotations=list()
        ),
    ):
        self.config = config


    def __iter__(self) -> Iterator[ModelType]:
        """This function implements application-level caching
        The cache is held in the __cache__ attribute,
        The un-finished iterator/generator is held in the __result_iterator__ attribute
        The method it expects to call to get the iterator is self._get_results()
        """
        if self.config.get('disable_cache', False):
            # Caching can be disabled via option
            for item in self._get_results():
                yield item
        else:
            if not hasattr(self, '__result_iterator__'):
                # Create a new iterator and cache if the iterator doesn't exist
                self.__result_iterator__ = self._get_results()
                self.__cache__: List[ModelType] = list()
            # Yield out of the cache
            for item in self.__cache__:
                yield item
            # Yield out of the iterator, expanding the cache as you go.
            for item in self.__result_iterator__:
                self.__cache__.append(item)
                yield item

    def _get_results(self) -> Iterator[ModelType]:
        raise NotImplementedError('Must be implemented by subclass')

    def __len__(self) -> int:
        # The default len function runs the iterator and counts. There may be 
        # more efficient ways to do it for any given subclass, but this is the
        # basic way
        return len(list(self))

    def __add__(self, other: Manager) -> QuerySet:
        return QuerySet([self, other])

    def __eq__(self, other) -> bool:
        return bool(self.config == other.config and type(self) == type(other))

    def __getitem__(self, key:Union[slice, int]) -> Union[Manager[ModelType], ModelType]:
        if isinstance(key, slice):
            if key.step != None:
                raise AttributeError("Step is not supported")
            start = key.start if key.start else 0
            start = len(self) + start if start < 0 else start
            stop = key.stop if key.stop else len(self)
            stop = len(self) + stop if stop < 0 else stop
            mger = self.offset(start + self.config["offset"])
            mger = mger.limit(stop - start)
            return mger
        return self.offset(key).first()

    def filter(self, *args, **kwargs) -> Manager[ModelType]:
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

    def order_by(self, *args) -> Manager[ModelType]:
        """Take arguments, and store in a special keyword argument called 'sort' """
        new_config = deepcopy(self.config)
        new_config["order_by"] = list(new_config["order_by"]) + list(args)
        return self.__class__(new_config)

    def set_options(self, **kwargs) -> Manager[ModelType]:
        new_config = deepcopy(self.config)
        new_config["options"] = {**new_config["options"], **kwargs}
        return self.__class__(new_config)

    def _clone(self):
        return self.__class__(deepcopy(self.config))

    def limit(self, limit) -> Manager[ModelType]:
        clone = self._clone()
        clone.config['limit'] = limit
        return clone

    def offset(self, offset) -> Manager[ModelType]:
        clone = self._clone()
        clone.config['offset'] = self.config['offset'] + offset
        return clone

    def get(self, *args, **kwargs) -> ModelType: 
        """Implement a new manager with the requested keywords, and if the length is 1,
        return that record, else raise an exception"""
        manager = self.filter(*args, **kwargs)
        if len(manager) > 1:
            raise ValueError("More than one document found!")
        return manager[0] # type: ignore

    # Manager Functions

    def count(self) -> int:
        return len(self)

    def first(self) -> ModelType:
        return next(iter(self))

    def all(self) -> Manager[ModelType]:
        return self

    def to_pandas(self, annotate=list()):
        import pandas as pd
        dicts = list()
        for i in iter(self):
            ordered_dict = OrderedDict(i)
            for a in annotate:
                ordered_dict[a] = resolve(i, a)
            dicts.append(ordered_dict)
        return pd.DataFrame.from_records(dicts)

    def explode(self, attribute) -> QuerySet:
        from itertools import chain
        return ListManager(chain.from_iterable(getattr(r, attribute, None) for r in self))

    def to_records(self) -> Iterator[OrderedDict]:
        for i in self:
            yield i.as_dict()
    
    def to_list(self) -> List[ModelType]:
        return list(self)
    
    # Values
    def values(self, *fields, **kw_fields) -> ValuesQuerySet:
        return ValuesQuerySet(self, *fields, **kw_fields)

    def values_list(self, *fields, flat=False, **kw_fields) -> ValuesListQuerySet:
        return ValuesListQuerySet(self, *fields, flat=flat, **kw_fields)

class ListManager(list, Manager[ModelType]):
    
    def _clone(self):
        return self

    def limit(self, limit):
        return ListManager(self[:limit])

    def offset(self, offset):
        return ListManager(self[offset:])

    def __getitem__(self, sl):
        result = list(self)[sl]
        if isinstance(sl, slice):
            return ListManager(result)
        else:
            return result

    @classmethod
    def empty(cls) -> ListManager:
        return cls(list())

class QuerySet(Manager[ModelType]):
    """
    Utility class that extends the Manager helper function to 
    any collection of Patent Client objects
    """

    def __init__(self, managers, limit=None, offset=0):
        if isinstance(managers, Manager):
            self.managers = [managers._clone(),]
        else:
            self.managers = [m._clone() for m in managers]
        self._limit = limit
        self._offset = offset

    def __getitem__(self, key:Union[slice, int]) -> Union[Manager[ModelType], ModelType]:
        if isinstance(key, slice):
            if key.step != None:
                raise AttributeError("Step is not supported")
            start = key.start if key.start else 0
            start = len(self) + start if start < 0 else start
            stop = key.stop if key.stop else len(self)
            stop = len(self) + stop if stop < 0 else stop
            mger = self.offset(start + self._offset)
            mger = mger.limit(stop - start)
            return mger
        return self.offset(key).first()

    def __iter__(self):
        if self.offset == 0 and self.limit == None:
            for manager in self.managers:
                yield from iter(manager)
        else:
            counter = 0
            max_items = self._offset + self._limit if self._limit else None
            for manager in self.managers:
                if counter + len(manager) < self._offset or (self._limit and counter >= self._limit):
                    """In these circumstances, don't yield objects"""
                    counter += len(manager)
                    continue
                else:
                    offset = max(self._offset - counter, 0)
                    manager = manager.offset(offset)
                    if self._limit:
                        limit = self._limit - counter
                        print(limit)
                        manager = manager.limit(limit)
                    yield from manager
                    counter += len(manager)

    def __len__(self):
        return sum(len(i) for i in self.managers)

    def __repr__(self):
        return f"<QuerySet({self.managers})>"

    def _clone(self):
        return self.__class__(self.managers)

    def limit(self, limit):
        clone = self._clone()
        clone._limit = limit
        return clone
    
    def offset(self, offset):
        clone = self._clone()
        clone._offset = clone._offset + offset
        return clone

    @classmethod
    def empty(cls) -> QuerySet:
        return cls(list())

class ValuesQuerySet(QuerySet):
    def __init__(self, managers, *fields, **kw_fields):
        super(ValuesQuerySet, self).__init__(managers)
        self.fields = {
            **{k:k for k in fields},
            **kw_fields
        }
    
    def _clone(self):
        return self.__class__(self.managers, **self.fields)

    def __iter__(self) -> Iterator[OrderedDict]:
        for item in super(ValuesQuerySet, self).__iter__():
            yield OrderedDict((k, resolve(item, v)) for k, v in self.fields.items())

class ValuesListQuerySet(ValuesQuerySet):
    def __init__(self, managers, *fields, flat=False, **kw_fields):
        super(ValuesListQuerySet, self).__init__(managers, *fields, **kw_fields)
        self.flat = flat
    
    def _clone(self):
        return self.__class__(self.managers, flat=self.flat, **deepcopy(self.fields))

    def __iter__(self):
        if self.flat and len(self.fields) > 1:
            raise ValueError("Flat only works with 1 field!")
        for data_dict in super(ValuesListQuerySet, self).__iter__():
            data = tuple(data_dict.values())
            yield data[0] if self.flat else data
