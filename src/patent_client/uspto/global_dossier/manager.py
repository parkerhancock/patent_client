from patent_client.util.base.manager import Manager

from .api import GlobalDossierApi
from .query import QueryBuilder
from .schema import DocumentListSchema
from .schema import GlobalDossierSchema

query_builder = QueryBuilder()

global_dossier_api = GlobalDossierApi()


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

    def get(self, *args, **kwargs):
        data = global_dossier_api.get_file(**query_builder.build_query(*args, **kwargs))
        return self.__schema__.load(data)


class GlobalDossierApplicationManager(GlobalDossierBaseManager):
    __schema__ = GlobalDossierSchema

    def get(self, *args, **kwargs):
        query = query_builder.build_query(*args, **kwargs)
        data = global_dossier_api.get_file(**query)
        gd_file = self.__schema__.load(data)
        if query["type_code"] == "application":
            return next(a for a in gd_file.applications if a.app_num in query["doc_number"])
        elif query["type_code"] == "publication":
            return next(a for a in gd_file.applications if any(p.pub_num in query["doc_number"] for p in a.pub_list))


class GlobalDossierDocument(GlobalDossierBaseManager):
    __schema__ = DocumentListSchema

    def get(self, country, doc_number, kind_code):
        data = global_dossier_api.get_doc_list(country, doc_number, kind_code)
        return self.__schema__.load(data)
