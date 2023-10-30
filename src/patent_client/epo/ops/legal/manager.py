from patent_client.util import Manager
from yankee.data import ListCollection

from .api import LegalApi
from .api import LegalAsyncApi
from .model import LegalEvent
from .schema import LegalSchema


class LegalManager(Manager):
    __schema__ = LegalSchema

    def get(self, doc_number, doc_type="publication", format="docdb") -> ListCollection[LegalEvent]:
        return self.__schema__.load(LegalApi.get_legal(doc_number, doc_type, format)).events

    async def aget(self, doc_number, doc_type="publication", format="docdb") -> ListCollection[LegalEvent]:
        return self.__schema__.load(await LegalAsyncApi.get_legal(doc_number, doc_type, format)).events
