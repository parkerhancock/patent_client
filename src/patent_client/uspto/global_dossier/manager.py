from patent_client.util.base.manager import Manager

from .api import GlobalDossierAsyncApi
from .query import QueryBuilder
from .schema import DocumentListSchema
from .schema import GlobalDossierSchema

query_builder = QueryBuilder()

global_dossier_async_api = GlobalDossierAsyncApi()


class GlobalDossierBaseManager(Manager):
    def filter(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")

    def order_by(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")

    def limit(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")

    def offset(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")


class GlobalDossierManager(GlobalDossierBaseManager):
    __schema__ = GlobalDossierSchema

    async def aget(self, *args, **kwargs):
        data = await global_dossier_async_api.get_file(**query_builder.build_query(*args, **kwargs))
        return self.__schema__.load(data)


class GlobalDossierApplicationManager(GlobalDossierBaseManager):
    __schema__ = GlobalDossierSchema

    async def aget(self, *args, **kwargs):
        query = query_builder.build_query(*args, **kwargs)
        data = await global_dossier_async_api.get_file(**query)
        gd_file = self.__schema__.load(data)
        if query["type_code"] == "application":
            return next(a for a in gd_file.applications if a.app_num in query["doc_number"])
        elif query["type_code"] == "publication":
            return next(a for a in gd_file.applications if any(p.pub_num in query["doc_number"] for p in a.pub_list))


class GlobalDossierDocument(GlobalDossierBaseManager):
    __schema__ = DocumentListSchema

    async def aget(self, country, doc_number, kind_code):
        data = await global_dossier_async_api.get_doc_list(country, doc_number, kind_code)
        return self.__schema__.load(data)
