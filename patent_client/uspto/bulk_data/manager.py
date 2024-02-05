import calendar
import datetime
import typing as tp

from .model import File
from .model import Product
from patent_client._async.uspto.bulk_data import BulkDataApi as BulkDataAsyncApi
from patent_client._sync.uspto.bulk_data import BulkDataApi as BulkDataSyncApi
from patent_client.util.manager import Manager


def date_ranges(start_date: datetime.date, end_date: datetime.date):
    # First range: start date to end of month
    end_of_month = datetime.datetime(
        start_date.year, start_date.month, calendar.monthrange(start_date.year, start_date.month)[1]
    )
    yield (start_date, end_of_month.date())

    # Full months between start and end date
    current_month = start_date.replace(day=1) + datetime.timedelta(days=32)
    while current_month.replace(day=1) < end_date.replace(day=1):
        last_day_of_month = current_month.replace(day=calendar.monthrange(current_month.year, current_month.month)[1])
        yield (current_month.replace(day=1), last_day_of_month)
        current_month += datetime.timedelta(days=32)

    # Last range: start of month to end date
    yield (end_date.replace(day=1), end_date)


class ProductManager(Manager):
    def filter_by_latest(self) -> tp.Iterator["Product"]:
        """Returns all products with Latest Files"""
        result = BulkDataSyncApi.get_latest()
        for product in result:
            yield Product.model_validate(product)

    async def afilter_by_latest(self) -> tp.AsyncIterator["Product"]:
        """Returns all products with Latest Files"""
        result = await BulkDataAsyncApi.get_latest()
        for product in result:
            yield Product.model_validate(product)

    def get_by_short_name(self, short_name) -> "Product":
        data = BulkDataSyncApi.get_by_short_name(short_name)
        return Product.model_validate(data)

    async def aget_by_short_name(self, short_name) -> "Product":
        data = await BulkDataAsyncApi.get_by_short_name(short_name)
        return Product.model_validate(data)

    def filter_by_name(self, short_name) -> tp.Iterator["Product"]:
        result = BulkDataSyncApi.get_by_name(short_name)
        for product in result:
            yield Product.model_validate(product)

    async def afilter_by_name(self, short_name) -> tp.AsyncIterator["Product"]:
        result = await BulkDataAsyncApi.get_by_name(short_name)
        for product in result:
            yield Product.model_validate(product)


class FileManager(Manager):
    def filter_by_short_name(self, short_name, from_date=None, to_date=None) -> tp.Iterator["File"]:
        if from_date is not None:
            from_date = from_date if isinstance(from_date, datetime.date) else datetime.date.fromisoformat(from_date)
        if to_date is not None:
            to_date = to_date if isinstance(to_date, datetime.date) else datetime.date.fromisoformat(to_date)
        if from_date is None or to_date is None:
            data = BulkDataSyncApi.get_by_short_name(short_name)
            product = Product.model_validate(data)
            from_date = from_date or product.from_date
            to_date = to_date or product.to_date
        for start_date, end_date in date_ranges(from_date, to_date):
            chunk = BulkDataSyncApi.get_by_short_name(short_name, from_date=start_date, to_date=end_date)
            prod = Product.model_validate(chunk)
            if prod.files:
                for file in prod.files:
                    yield file

    async def afilter_by_short_name(self, short_name, from_date=None, to_date=None) -> tp.AsyncIterator["File"]:
        if from_date is not None:
            from_date = from_date if isinstance(from_date, datetime.date) else datetime.date.fromisoformat(from_date)
        if to_date is not None:
            to_date = to_date if isinstance(to_date, datetime.date) else datetime.date.fromisoformat(to_date)
        if from_date is None or to_date is None:
            product = await BulkDataAsyncApi.get_by_short_name(short_name)
            from_date = from_date or product.from_date
            to_date = to_date or product.to_date
        for start_date, end_date in date_ranges(from_date, to_date):
            chunk = await BulkDataAsyncApi.get_by_short_name(short_name, from_date=start_date, to_date=end_date)
            prod = Product.model_validate(chunk)
            if prod.files:
                for file in prod.files:
                    yield file
