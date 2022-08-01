from patent_client.util import Manager

from .api import FamilyApi

class OpsFamilyManager(Manager):

    def _get_results(self) -> Iterator[ModelType]:
        return FamilyApi.get_family()