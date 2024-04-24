from .api import FamilyAsyncApi
from .model import Family
from .schema import FamilySchema
from patent_client.util.manager import AsyncManager


class FamilyManager(AsyncManager[Family]):
    __schema__ = FamilySchema

    async def get(self, doc_number):
        return await FamilyAsyncApi.get_family(
            doc_number, doc_type="publication", format="docdb"
        )
