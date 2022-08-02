import logging
from io import BytesIO
from warnings import warn

import lxml.etree as ET

from patent_client.epo.ops.session import session

from .model import BiblioResult
from .model import Claims
from .model import Description
from .model import Images
from .model import Search
from .schema import BiblioResultSchema
from .schema import ClaimsSchema
from .schema import DescriptionSchema
from .schema import ImagesSchema
from .schema import SearchSchema

logger = logging.getLogger(__name__)


class PublishedBiblioApi:
    schema = BiblioResultSchema()

    @classmethod
    def get_constituents(cls, number, doc_type="publication", format="docdb", constituents=("biblio",)) -> BiblioResult:
        """Published Data Constituents API
        number: document number to search
        doc_type: document type (application / publication)
        format: document number format (original / docdb / epodoc)
        constituents: what data to retrieve. Can be combined. (biblio / abstract / full-cycle)

        """
        base_url = f"http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/{format}/{number}/"
        if isinstance(constituents, str):
            constituents = (constituents,)
        url = base_url + ",".join(constituents)
        response = session.get(url)
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        return cls.schema.load(tree)

    @classmethod
    def get_biblio(cls, number, doc_type="publication", format="docdb") -> BiblioResult:
        return cls.get_constituents(number, doc_type, format, constituents="biblio")

    @classmethod
    def get_abstract(cls, number, doc_type="publication", format="docdb") -> BiblioResult:
        return cls.get_constituents(number, doc_type, format, constituents="abstract")

    @classmethod
    def get_full_cycle(cls, number, doc_type="publication", format="docdb") -> BiblioResult:
        return cls.get_constituents(number, doc_type, format, constituents="full-cycle")


class PublishedFulltextApi:
    fulltext_jurisdictions = "EP, WO, AT, BE, BG, CA, CH, CY, CZ, DK, EE, ES, FR, GB, GR, HR, IE, IT, LT, LU, MC, MD, ME, NO, PL, PT, RO, RS, SE, SK".split(
        ", "
    )
    desciption_schema = DescriptionSchema()
    claims_schema = ClaimsSchema()

    @classmethod
    def get_fulltext_result(cls, number, doc_type="publication", format="docdb", inquiry="fulltext"):
        """Published Fulltext API
        number: document number to search
        doc_type: document type (application / publication)
        format: document number format (original / docdb / epodoc)
        inquiry: what data to retrieve. Can be combined. (fulltext / description / claims)

        """
        url = f"http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/{format}/{number}/{inquiry}"
        if number[:2] not in cls.fulltext_jurisdictions:
            raise ValueError(
                f"Fulltext Is Not Available For Country Code {number[:2]}. Fulltext is only available in {', '.join(cls.fulltext_jurisdictions)}"
            )
        response = session.get(url)
        response.raise_for_status
        return response.text

    @classmethod
    def get_description(cls, number, doc_type="publication", format="docdb") -> Description:
        text = cls.get_fulltext_result(number, doc_type="publication", format="docdb", inquiry="description")
        tree = ET.fromstring(text.encode())
        return cls.desciption_schema.load(tree)

    @classmethod
    def get_claims(cls, number, doc_type="publication", format="docdb") -> Claims:
        text = cls.get_fulltext_result(number, doc_type="publication", format="docdb", inquiry="claims")
        tree = ET.fromstring(text.encode())
        return cls.claims_schema.load(tree)


class PublishedSearchApi:
    schema = SearchSchema()

    @classmethod
    def search(cls, query, start=1, end=100) -> Search:
        base_url = "http://ops.epo.org/3.2/rest-services/published-data/search"
        range = f"{start}-{end}"
        logger.debug(f"OPS Search Endpoint - Query: {query}\nRange: {start}-{end}")
        response = session.get(base_url, params={"q": query, "Range": range})
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        result = cls.schema.load(tree)
        if result.num_results == 10000:
            warn("Actual Number of Results is Greater Than 10,000 - OPS stops counting after 10,000")
        return result


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
            f"https://ops.epo.org/3.2/rest-services/{link}.{image_format}", params={"Range": page_number}, stream=True
        )
        response.raise_for_status()
        return BytesIO(response.raw.read())


class PublishedApi:
    biblio = PublishedBiblioApi
    fulltext = PublishedFulltextApi
    search = PublishedSearchApi
    images = PublishedImagesApi
