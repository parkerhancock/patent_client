import logging
from io import BytesIO
from warnings import warn

import lxml.etree as ET
from patent_client.epo.ops.session import session
from patent_client.util.base.collections import ListManager
from yankee.util import AttrDict

from .model import BiblioResult
from .model import Claims
from .model import Description
from .model import Images
from .model import Search
from .schema import BiblioResultSchema
from .schema import ClaimsSchema
from .schema import DescriptionSchema
from .schema import ImagesSchema
# from .search import SearchSchema
from .schema import EPRegisterSearchSchema

logger = logging.getLogger(__name__)


class EpoRegisterException(Exception):
    pass


class EPRegisterApi:
    search_schema = EPRegisterSearchSchema()
    retrieval_schema = None

    reference_types = ("publication", "application", "priority")
    constituents = ("biblio", "procedural-steps", "events")

    @classmethod
    def search(cls, query, start=1, end=100) -> Search:        
        base_url = "http://ops.epo.org/3.2/rest-services/register/search"
        range = f"{start}-{end}"
        logger.debug(f"OPS Search Endpoint - Query: {query}\nRange: {start}-{end}")
        response = session.get(base_url, params={"Range": range, "q": query})
        
        # If a search returns no results, EPO returns a 404 not found code.
        if response.status_code == 404:
            return AttrDict.convert(
                {
                    "query": query,
                    "num_results": 0,
                    "begin": start,
                    "end": end,
                    "results": ListManager(),
                }
            )       
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        result = cls.schema.load(tree)
        if result.num_results == 10000:
             warn("Actual Number of Results is Greater Than 10,000 - OPS stops counting after 10,000")
        return result

    @classmethod
    def retrieve(cls, doc_number, reference_type="publication", constituents=("biblio",)):
        # Note - Register only supports the EPODOC number format
        if reference_type not in cls.reference_types:
            raise EpoRegisterException(f"{reference_type} is not a supported reference_type, must be in {', '.join(cls.reference_types)}")
        if not all(c in c.constituents for c in constituents):
            raise EpoRegisterException(f"{constituents} is not an available constiuent(s), must be a tuple of {', '.join(cls.constituents)}")
        url = f"http://ops.epo.org/3.2/rest-services/register/{reference_type}/epodoc/{doc_number}/{','.join(constituents)}"





###############################
###############################

class PublishedImagesApi:
    schema = ImagesSchema()

    @classmethod
    def get_images(cls, number, doc_type="publication", format="docdb") -> Images:
        base_url = f"http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/{format}/{number}/images"
        response = session.get(base_url)
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        return cls.schema.load(tree)

    @classmethod
    def get_page_image(cls, country, number, kind, image_type, page_number, image_format="pdf"):
        response = session.get(
            f"https://ops.epo.org/3.2/rest-services/published-data/images/{country}/{number}/{kind}/{image_type}.{image_format}",
            params={"Range": page_number},
            stream=True,
        )
        response.raise_for_status()
        return BytesIO(response.raw.read())

    @classmethod
    def get_page_image_from_link(cls, link, page_number, image_format="pdf"):
        response = session.get(
            f"https://ops.epo.org/3.2/rest-services/{link}.{image_format}",
            params={"Range": page_number},
            stream=True,
        )
        response.raise_for_status()
        return BytesIO(response.raw.read())


class PublishedApi:
    biblio = PublishedBiblioApi
    fulltext = PublishedFulltextApi
    # change here
    search = EPRegisterSearchApi
    #
    images = PublishedImagesApi
