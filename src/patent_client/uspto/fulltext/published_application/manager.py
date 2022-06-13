from ..manager import FullTextManager
from ..manager import ImageManager
from .model import PublishedApplicationResult
from .schema import PublishedApplicationImageSchema
from .schema import PublishedApplicationSchema
from .settings import PUBLICATION_URL
from .settings import SEARCH_FIELDS
from .settings import SEARCH_PARAMS
from .settings import SEARCH_URL


class PublishedApplicationManager(FullTextManager):
    __schema__ = PublishedApplicationSchema
    search_fields = SEARCH_FIELDS
    search_params = SEARCH_PARAMS
    search_url = SEARCH_URL
    pub_base_url = PUBLICATION_URL
    result_model = PublishedApplicationResult


class PublishedApplicationImageManager(ImageManager):
    __schema__ = PublishedApplicationImageSchema
    BASE_URL = "https://pdfaiw.uspto.gov/.aiw"
