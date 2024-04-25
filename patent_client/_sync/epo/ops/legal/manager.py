# ********************************************************************************
# *         WARNING: This file is automatically generated by unasync.py.         *
# *                             DO NOT MANUALLY EDIT                             *
# *          Source File: patent_client/_async/epo/ops/legal/manager.py          *
# ********************************************************************************

from yankee.data import ListCollection

from patent_client.util.manager import Manager

from .api import LegalApi
from .model import LegalEvent
from .schema import LegalSchema


class LegalManager(Manager):
    __schema__ = LegalSchema

    def get(
        self, doc_number, doc_type="publication", format="docdb"
    ) -> ListCollection[LegalEvent]:
        return self.__schema__.load(
            LegalApi.get_legal(doc_number, doc_type, format)
        ).events