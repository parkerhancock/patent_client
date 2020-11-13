from ..manager import FullTextManager, ImageManager
from .settings import SEARCH_PARAMS, SEARCH_FIELDS, SEARCH_URL, PUBLICATION_URL
from .schema import PublishedApplicationSchema, PublishedApplicationImageSchema
from .model import PublishedApplicationResult

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