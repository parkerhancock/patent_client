from patent_client.util.manager import AsyncManager

from .api import GlobalDossierApi
from .query import QueryBuilder

query_builder = QueryBuilder()

global_dossier_api = GlobalDossierApi()


class GlobalDossierBaseManager(AsyncManager):
    def filter(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")

    def order_by(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")

    def limit(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")

    def offset(self, *args, **kwargs):
        raise NotImplementedError("GlobalDossier can only retrieve using the GET interface")


class GlobalDossierManager(GlobalDossierBaseManager):
    async def get(self, *args, **kwargs):
        return await global_dossier_api.get_file(**query_builder.build_query(*args, **kwargs))


class GlobalDossierApplicationManager(GlobalDossierBaseManager):
    async def get(self, *args, **kwargs):
        query = query_builder.build_query(*args, **kwargs)
        gd_file = await global_dossier_api.get_file(**query)
        if query["type_code"] == "application":
            return next(a for a in gd_file.applications if a.app_num in query["doc_number"])
        elif query["type_code"] == "publication":
            return next(
                a
                for a in gd_file.applications
                if any(p.pub_num in query["doc_number"] for p in a.pub_list)
            )


class DocumentListManager(GlobalDossierBaseManager):
    async def get(self, country, doc_number, kind_code):
        return await global_dossier_api.get_doc_list(country, doc_number, kind_code)
