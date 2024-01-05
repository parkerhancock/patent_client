import datetime
import typing as tp

from ..http_client import PatentClientAsyncHttpClient


class BulkDataApi:
    http_client = PatentClientAsyncHttpClient()

    @classmethod
    async def get_latest(cls) -> tp.Any:
        """Returns all products with Latest Files"""
        response = await cls.http_client.get("https://bulkdata.uspto.gov:443/BDSS-API/products/all/latest")
        response.raise_for_status()
        return response.json()

    @classmethod
    async def get_by_name(
        cls,
        product_name: str,
        from_date: tp.Optional[datetime.date] = None,
        to_date: tp.Optional[datetime.date] = None,
        max_files: int = 20,
    ) -> tp.Any:
        """Returns files associated with products (of level PRODUCT) based on their full or partial names."""
        params = dict(hierarchy=False)
        if from_date:
            if isinstance(from_date, str):
                from_date = datetime.date.fromisoformat(from_date)
            params["fromYear"] = from_date.year
            params["fromMonth"] = from_date.month
            params["fromDay"] = from_date.day
        if to_date:
            if isinstance(to_date, str):
                to_date = datetime.date.fromisoformat(to_date)
            params["toYear"] = to_date.year
            params["toMonth"] = to_date.month
            params["toDay"] = to_date.day
        params["maxFiles"] = max_files
        response = await cls.http_client.get(
            f"https://bulkdata.uspto.gov:443/BDSS-API/products/byname/{product_name}", params=params
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    async def get_popular(cls) -> tp.Any:
        """Returns popular products along with latest files."""
        response = await cls.http_client.get("https://bulkdata.uspto.gov:443/BDSS-API/products/popular")
        response.raise_for_status()
        return response.json()

    @classmethod
    async def get_by_short_name(
        cls,
        product_name: str,
        from_date: tp.Optional[datetime.date | str] = None,
        to_date: tp.Optional[datetime.date | str] = None,
        max_files: int = 20,
    ) -> tp.Any:
        """Returns files associated with products (of level PRODUCT) based on their full or partial names."""
        params = dict()
        if from_date:
            if isinstance(from_date, str):
                from_date = datetime.date.fromisoformat(from_date)
            params["fromYear"] = from_date.year
            params["fromMonth"] = from_date.month
            params["fromDay"] = from_date.day
        if to_date:
            if isinstance(to_date, str):
                to_date = datetime.date.fromisoformat(to_date)
            params["toYear"] = to_date.year
            params["toMonth"] = to_date.month
            params["toDay"] = to_date.day
        response = await cls.http_client.get(
            f"https://bulkdata.uspto.gov:443/BDSS-API/products/{product_name}", params=params
        )
        response.raise_for_status()
        return response.json()
