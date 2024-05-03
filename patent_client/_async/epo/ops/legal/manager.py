from yankee.data import ListCollection

from patent_client.util.manager import AsyncManager

from .api import LegalApi
from .model import LegalEvent
from .schema import LegalSchema


class LegalManager(AsyncManager):
    __schema__ = LegalSchema

    async def get(
        self, doc_number, doc_type="publication", format="docdb"
    ) -> ListCollection[LegalEvent]:
        return self.__schema__.load(await LegalApi.get_legal(doc_number, doc_type, format)).events
