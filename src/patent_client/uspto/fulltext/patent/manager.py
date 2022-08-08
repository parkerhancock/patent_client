from ..manager import FullTextManager
from ..manager import ImageManager
from .model import PatentResult
from .schema import PatentImageSchema, PatentResultPageSchema, PatentSchema
from .settings import PUBLICATION_URL
from .settings import SEARCH_FIELDS
from .settings import SEARCH_PARAMS
from .settings import SEARCH_URL


class PatentManager(FullTextManager):
    __schema__ = PatentSchema()
    search_fields = SEARCH_FIELDS
    search_params = SEARCH_PARAMS
    search_url = SEARCH_URL
    pub_base_url = PUBLICATION_URL
    result_model = PatentResult
    result_page_parser = PatentResultPageSchema()


class PatentImageManager(ImageManager):
    __schema__ = PatentImageSchema()
    BASE_URL = "https://pdfpiw.uspto.gov"
    DL_URL = "https://pdfpiw.uspto.gov/fdd/{pdf_id}/0.pdf"
