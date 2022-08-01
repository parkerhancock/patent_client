from patent_client.util import Model, Manager
from patent_client.epo.ops import OpsApi
from patent_client.epo.ops.published.cql import generate_query

class Inpadoc(Manager):
    page_size = 20
    primary_key = "publication"

    def _get_results(self) -> Iterator[ModelType]:
        query = generate_query(self.config['filter'])
        return OpsApi.published.search.search(query)

    def get(self, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            return OpsApi.published.data.get_biblio(args[0])
        else:
            return super().get(*args, **kwargs)

class Inpadoc