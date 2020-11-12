from ..manager import FullTextManager, ImageManager
from .settings import SEARCH_FIELDS, SEARCH_PARAMS, SEARCH_URL, PUBLICATION_URL
from .schema import PatentSchema, PatentImageSchema
from .model import PatentResult

class PatentManager(FullTextManager):
    __schema__ = PatentSchema
    search_fields = SEARCH_FIELDS
    search_params = SEARCH_PARAMS
    search_url = SEARCH_URL
    pub_base_url = PUBLICATION_URL
    result_model = PatentResult

class PatentImageManager(ImageManager):
    __schema__ = PatentImageSchema
    BASE_URL = "https://pdfpiw.uspto.gov/.piw"

