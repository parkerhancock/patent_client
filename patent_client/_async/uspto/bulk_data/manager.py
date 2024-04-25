import calendar
import datetime
import typing as tp

from patent_client.util.manager import AsyncManager

from .api import BulkDataApi

if tp.TYPE_CHECKING:
    from .model import File, Product


def date_ranges(start_date: datetime.date, end_date: datetime.date):
    # First range: start date to end of month
    end_of_month = datetime.datetime(
        start_date.year,
        start_date.month,
        calendar.monthrange(start_date.year, start_date.month)[1],
    )
    yield (start_date, end_of_month.date())

    # Full months between start and end date
    current_month = start_date.replace(day=1) + datetime.timedelta(days=32)
    while current_month.replace(day=1) < end_date.replace(day=1):
        last_day_of_month = current_month.replace(
            day=calendar.monthrange(current_month.year, current_month.month)[1]
        )
        yield (current_month.replace(day=1), last_day_of_month)
        current_month += datetime.timedelta(days=32)

    # Last range: start of month to end date
    yield (end_date.replace(day=1), end_date)


class ProductManager(AsyncManager):
    async def filter_by_latest(self) -> tp.AsyncIterator["Product"]:
        """Returns all products with Latest Files"""
        result = await BulkDataApi.get_latest()
        for product in result:
            yield product

    async def get_by_short_name(self, short_name) -> "Product":
        result = await BulkDataApi.get_by_short_name(short_name)
        return result

    async def filter_by_name(self, short_name) -> tp.AsyncIterator["Product"]:
        result = await BulkDataApi.get_by_name(short_name)
        for product in result:
            yield product


class FileManager(AsyncManager):
    async def filter_by_short_name(
        self, short_name, from_date=None, to_date=None
    ) -> tp.AsyncIterator["File"]:
        if from_date is not None:
            from_date = (
                from_date
                if isinstance(from_date, datetime.date)
                else datetime.date.fromisoformat(from_date)
            )
        if to_date is not None:
            to_date = (
                to_date
                if isinstance(to_date, datetime.date)
                else datetime.date.fromisoformat(to_date)
            )
        if from_date is None or to_date is None:
            product = await BulkDataApi.get_by_short_name(short_name)
            from_date = from_date or product.from_date
            to_date = to_date or product.to_date
        for start_date, end_date in date_ranges(from_date, to_date):
            chunk = await BulkDataApi.get_by_short_name(
                short_name, from_date=start_date, to_date=end_date
            )
            if chunk.files:
                for file in chunk.files:
                    yield file
