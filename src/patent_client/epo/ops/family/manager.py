from patent_client.util import Manager

from .api import FamilyAsyncApi
from .schema import FamilySchema


class FamilyManager(Manager):
    __schema__ = FamilySchema

    async def aget(self, doc_number):
        return self.__schema__.load(await FamilyAsyncApi.get_family(doc_number, doc_type="publication", format="docdb"))
