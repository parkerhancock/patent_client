from .model import DocumentList
from .model import GlobalDossier
from .query import QueryBuilder
from patent_client._async.uspto.global_dossier import GlobalDossierApi as GlobalDossierAsyncApi
from patent_client._sync.uspto.global_dossier import GlobalDossierApi as GlobalDossierSyncApi
from patent_client.util.manager import Manager

query_builder = QueryBuilder()


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
    async def aget(self, *args, **kwargs):
        data = await GlobalDossierAsyncApi.get_dossier(**query_builder.build_query(*args, **kwargs))
        return GlobalDossier.model_validate(data)

    def get(self, *args, **kwargs):
        data = GlobalDossierSyncApi.get_dossier(**query_builder.build_query(*args, **kwargs))
        return GlobalDossier.model_validate(data)


class GlobalDossierApplicationManager(GlobalDossierBaseManager):
    async def aget(self, *args, **kwargs):
        query = query_builder.build_query(*args, **kwargs)
        data = await GlobalDossierAsyncApi.get_dossier(**query)
        gd_file = GlobalDossier.model_validate(data)
        if query["type_code"] == "application":
            return next(a for a in gd_file.applications if a.app_num in query["doc_number"])
        elif query["type_code"] == "publication":
            return next(a for a in gd_file.applications if any(p.pub_num in query["doc_number"] for p in a.pub_list))

    def get(self, *args, **kwargs):
        query = query_builder.build_query(*args, **kwargs)
        data = GlobalDossierSyncApi.get_dossier(**query)
        gd_file = GlobalDossier.model_validate(data)
        if query["type_code"] == "application":
            return next(a for a in gd_file.applications if a.app_num in query["doc_number"])
        elif query["type_code"] == "publication":
            return next(a for a in gd_file.applications if any(p.pub_num in query["doc_number"] for p in a.pub_list))


class DocumentListManager(GlobalDossierBaseManager):
    async def aget(self, country, doc_number, kind_code):
        data = await GlobalDossierAsyncApi.get_doc_list(country, doc_number, kind_code)
        return DocumentList.model_validate(data)

    def get(self, country, doc_number, kind_code):
        data = GlobalDossierSyncApi.get_doc_list(country, doc_number, kind_code)
        return DocumentList.model_validate(data)
