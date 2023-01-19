from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from itertools import chain
from typing import Generic
from typing import Iterator
from typing import TypeVar
from typing import Union

from yankee.data import Collection

ModelType = TypeVar("ModelType")


class ManagerConfig:
    """
    Manager Configuration Class

    This class holds configuration information for a manager
    """

    def __init__(self):
        self.filter = OrderedDict()
        self.order_by = list()
        self.options = dict()
        self.limit = None
        self.offset = 0
        self.annotations = list()

    def __eq__(self, other):
        return (
            self.filter == other.filter
            and self.order_by == other.order_by
            and self.options == other.options
            and self.limit == other.limit
            and self.offset == other.offset
            and self.annotations == other.annotations
        )


class Manager(Collection, Generic[ModelType]):
    """
    Manager Class

    This class is essentially a configurable generator. It is intended to be initialized
    as an empty object at Model.objects. Users can then call methods to modify the manager.
    All methods should return a brand-new manager with the appropriate parameters re-set.
    The manager's attributes are stored in a dictionary at Manager.config.

    """

    primary_key: str = ""

    def __init__(self, config=None):
        self.config = config or ManagerConfig()
        if callable(self.__schema__):
            self.__schema__ = self.__schema__()

    # Manager Iteration / Slicing

    def __iter__(self) -> Iterator[ModelType]:
        for item in self._get_results():
            yield item

    def _get_results(self) -> Iterator[ModelType]:
        raise NotImplementedError("Must be implemented by subclass")

    def __getitem__(self, key: Union[slice, int]) -> Union[Manager[ModelType], ModelType]:
        if isinstance(key, slice):
            if key.step != None:
                raise AttributeError("Step is not supported")
            start = key.start if key.start else 0
            start = len(self) + start if start < 0 else start
            stop = key.stop if key.stop else len(self)
            stop = len(self) + stop if stop < 0 else stop
            mger = self.offset(start + self.config.offset)
            mger = mger.limit(stop - start)
            return mger
        return self.offset(key).first()

    # Basic Manager Attributes

    def __len__(self) -> int:
        # The default len function runs the iterator and counts. There may be
        # more efficient ways to do it for any given subclass, but this is the
        # basic way
        return len(list(self))

    def __eq__(self, other) -> bool:
        return bool(self.config == other.config and type(self) == type(other))

    def __add__(self, other):
        return Collection(chain(self, other))

    # Manager Modification Functions

    def filter(self, *args, **kwargs) -> Manager[ModelType]:
        """Apply a new filtering condition"""
        mger = deepcopy(self)
        if args:
            kwargs[self.primary_key] = args
        update_values = OrderedDict()
        for key in sorted(kwargs.keys()):
            update_values[key] = kwargs[key]
        mger.config.filter.update(update_values)
        return mger

    def order_by(self, *args) -> Manager[ModelType]:
        """Specify the order that argument should be returned in"""
        mger = deepcopy(self)
        mger.config.order_by = args
        return mger

    def option(self, **kwargs) -> Manager[ModelType]:
        """Set a key:value option on the manager"""
        mger = deepcopy(self)
        mger.config.options = {**mger.config.options, **kwargs}
        return mger

    def limit(self, limit) -> Manager[ModelType]:
        """Limit the number of records that are returned"""
        mger = deepcopy(self)
        mger.config.limit = limit
        return mger

    def offset(self, offset) -> Manager[ModelType]:
        """Specify the number of records from the beginning from which to apply an offset"""
        mger = deepcopy(self)
        mger.config.offset = self.config.offset + offset
        return mger

    def get(self, *args, **kwargs) -> ModelType:
        """If the critera results in a single record, return it, else raise an exception"""
        mger = self.filter(*args, **kwargs)
        if len(mger) > 1:
            raise ValueError("More than one document found!")
        if len(mger) == 0:
            raise ValueError("No documents found!")
        return mger[0]  # type: ignore

    # Basic Manager Fetching

    def count(self) -> int:
        """Returns number of records in the QuerySet. Alias for len(self)"""
        return len(self)

    def first(self) -> ModelType:
        """Get the first object in the manager"""
        return next(iter(self))

    def all(self) -> Manager[ModelType]:
        """Return self. Does nothing"""
        return self
