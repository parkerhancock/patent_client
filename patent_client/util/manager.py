from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from itertools import chain
from typing import TYPE_CHECKING, AsyncIterator, Generic, Iterator, TypeVar, Union

from typing_extensions import Self
from yankee.data import Collection

if TYPE_CHECKING:
    pass

ModelType = TypeVar("ModelType")


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ManagerConfig:
    """
    Manager Configuration Class

    This class is designed to store and manage configuration settings for a manager object. It allows for the customization of query parameters and options to tailor data retrieval processes. The attributes of this class include:

    Attributes:
        filter (OrderedDict[str, list]): An ordered dictionary to store filter conditions for queries. The keys represent the field names, and the values represent the filter criteria.
        order_by (list[tuple[str, OrderDirection]]): A list of tuples specifying the ordering of query results. Each tuple contains a field name and the direction ('asc' for ascending, 'desc' for descending) of the sort.
        options (dict[str, str]): A dictionary to store additional options that may affect the query or its results.
        limit (int | None): An optional integer specifying the maximum number of results to return. If None, no limit is applied.
        offset (int): An integer specifying the offset from the start of the result set. Used for pagination.
        annotations (list[tuple[str, str]]): A list of tuples for annotating the results with extra information. Each tuple contains a field name and an annotation.

    The class also includes a method for comparing two `ManagerConfig` instances for equality based on their attributes.
    """

    def __init__(self):
        self.filter: OrderedDict[str, list] = OrderedDict()
        self.order_by: list[tuple[str, OrderDirection]] = list()
        self.options: dict[str, str] = dict()
        self.limit: int | None = None
        self.offset: int = 0
        self.annotations: list[tuple[str, str]] = list()

    def __eq__(self, other):
        return (
            self.filter == other.filter
            and self.order_by == other.order_by
            and self.options == other.options
            and self.limit == other.limit
            and self.offset == other.offset
            and self.annotations == other.annotations
        )


class BaseManager(Collection, Generic[ModelType]):
    default_filter: str = ""

    def __init__(self, config=None):
        self.config = config or ManagerConfig()

    def __eq__(self, other) -> bool:
        return bool(self.config == other.config and isinstance(self, type(other)))

    def __add__(self, other):
        return Collection(chain(self, other))

    # Manager Modification Functions

    def filter(self, *args, **kwargs) -> Self:
        """Apply a new filtering condition"""
        mger = deepcopy(self)
        if args:
            kwargs[self.default_filter] = args

        for key, value in kwargs.items():
            if isinstance(value, (str, dict, int, float)):
                kwargs[key] = [value]
            else:
                kwargs[key] = list(value)

        for key, value in kwargs.items():
            if key in mger.config.filter:
                mger.config.filter[key].extend(value)
            else:
                mger.config.filter[key] = value

        return mger

    def order_by(self, *args) -> Self:
        """Specify the order that argument should be returned in"""
        mger = deepcopy(self)
        mger.config.order_by = args
        return mger

    def option(self, **kwargs) -> Self:
        """Set a key:value option on the manager"""
        mger = deepcopy(self)
        mger.config.options = {**mger.config.options, **kwargs}
        return mger

    def limit(self, limit) -> Self:
        """Limit the number of records that are returned"""
        mger = deepcopy(self)
        mger.config.limit = limit
        return mger

    def offset(self, offset) -> Self:
        """Specify the number of records from the beginning from which to apply an offset"""
        mger = deepcopy(self)
        mger.config.offset = self.config.offset + offset
        return mger

    # Basic Manager Fetching

    def count(self) -> int:
        """Returns number of records in the QuerySet. Alias for len(self)"""
        return len(self)

    def all(self) -> Manager[ModelType]:
        """Return self. Does nothing"""
        return self


class Manager(BaseManager, Generic[ModelType]):
    """
    Manager Class (Synchronous)

    This class is essentially a configurable generator. It is intended to be initialized
    as an empty object at Model.objects. Users can then call methods to modify the manager.
    All methods should return a brand-new manager with the appropriate parameters re-set.
    The manager's attributes are stored in a dictionary at Manager.config.

    """

    default_filter: str = ""

    def __init__(self, config=None):
        self.config = config or ManagerConfig()

    # Manager Iteration / Slicing

    def __iter__(self) -> Iterator[ModelType]:
        return self._get_results()

    def __getitem__(self, key: Union[slice, int]) -> Union[Manager[ModelType], ModelType]:
        if isinstance(key, slice):
            if key.step is not None:
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
        return self.count()

    def __eq__(self, other) -> bool:
        return bool(self.config == other.config and isinstance(self, type(other)))

    def __add__(self, other):
        return Collection(chain(self, other))

    def first(self) -> ModelType:
        """Get the first object in the manager"""
        return next(self.limit(1).__iter__())

    def get(self, *args, **kwargs) -> ModelType:
        """If the critera results in a single record, return it, else raise an exception"""
        mger = self.filter(*args, **kwargs)
        length = len(mger)
        if length > 1:
            raise ValueError("More than one document found!")
        if length == 0:
            raise ValueError("No documents found!")
        return mger.first()


class AsyncManager(BaseManager, Generic[ModelType]):
    """
    Manager Class (Asynchronous)

    This class is essentially a configurable generator. It is intended to be initialized
    as an empty object at Model.objects. Users can then call methods to modify the manager.
    All methods should return a brand-new manager with the appropriate parameters re-set.
    The manager's attributes are stored in a dictionary at Manager.config.

    """

    default_filter: str = ""

    def __init__(self, config=None):
        self.config = config or ManagerConfig()

    # Manager Iteration / Slicing

    def __aiter__(self) -> AsyncIterator[ModelType]:
        return self._get_results()

    async def _get_results(self) -> AsyncIterator[ModelType]:
        raise NotImplementedError(
            f"This method must be defined in a subclass of {self.__class__.__name__}"
        )

    async def __getitem__(self, key: Union[slice, int]) -> Union[Manager[ModelType], ModelType]:
        if isinstance(key, slice):
            if key.step is not None:
                raise AttributeError("Step is not supported")
            count = await self.count()
            start = key.start if key.start else 0
            start = count + start if start < 0 else start
            stop = key.stop if key.stop else count
            stop = count + stop if stop < 0 else stop
            mger = self.offset(start + self.config.offset)
            mger = mger.limit(stop - start)
            return mger
        return await self.offset(key).first()

    # Basic Manager Attributes

    def __len__(self) -> int:
        raise NotImplementedError(
            f"This method is not implemented for the AsyncManager class. Use await {self.__class__.__name__}.count() instead."
        )

    async def count(self) -> int:
        """Returns number of records in the QuerySet. Alias for len(self)"""
        return NotImplemented(
            f"This method must be defined in a subclass of {self.__class__.__name__}"
        )

    async def len(self) -> int:
        """Returns number of records in the QuerySet. Alias for self.count()"""
        return await self.count()

    async def first(self) -> ModelType:
        """Get the first object in the manager"""
        try:
            return await anext(self.limit(1).__aiter__())
        except NameError:  # anext was added in 3.10
            async for doc in self.limit(1):
                return doc

    async def get(self, *args, **kwargs) -> ModelType:
        """If the critera results in a single record, return it, else raise an exception"""
        mger = self.filter(*args, **kwargs)
        length = await mger.count()
        if length > 1:
            raise ValueError("More than one document found!")
        if length == 0:
            raise ValueError("No documents found!")
        return await mger.first()

    async def to_list(self) -> list[ModelType]:
        """Return a list of all objects in the manager"""
        return [item async for item in self]
