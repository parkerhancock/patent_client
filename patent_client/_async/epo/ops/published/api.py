import logging
from io import BytesIO

from yankee.data import AttrDict

from ..session import session
from .model.biblio import BiblioResult
from .model.fulltext import Claims, Description
from .model.images import Images
from .model.search import Search

logger = logging.getLogger(__name__)


class PublishedBiblioApi:
    @classmethod
    async def get_constituents(
        cls, number, doc_type="publication", format="docdb", constituents=("biblio",)
    ):
        """Published Data Constituents API
        number: document number to search
        doc_type: document type (application / publication)
        format: document number format (original / docdb / epodoc)
        constituents: what data to retrieve. Can be combined. (biblio / abstract / full-cycle)

        """
        base_url = (
            f"http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/{format}/{number}/"
        )
        if isinstance(constituents, str):
            constituents = (constituents,)
        url = base_url + ",".join(constituents)
        response = await session.get(url)
        return response.text

    @classmethod
    async def get_biblio(cls, number, doc_type="publication", format="docdb") -> "BiblioResult":
        text = await cls.get_constituents(number, doc_type, format, constituents="biblio")
        return BiblioResult.model_validate(text)

    @classmethod
    async def get_abstract(cls, number, doc_type="publication", format="docdb"):
        return await cls.get_constituents(number, doc_type, format, constituents="abstract")

    @classmethod
    async def get_full_cycle(cls, number, doc_type="publication", format="docdb"):
        return await cls.get_constituents(number, doc_type, format, constituents="full-cycle")


class PublishedFulltextApi:
    fulltext_jurisdictions = "EP, WO, AT, BE, BG, CA, CH, CY, CZ, DK, EE, ES, FR, GB, GR, HR, IE, IT, LT, LU, MC, MD, ME, NO, PL, PT, RO, RS, SE, SK".split(
        ", "
    )

    @classmethod
    async def get_fulltext_result(
        cls, number, doc_type="publication", format="docdb", inquiry="fulltext"
    ):
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
        response = await session.get(url)
        response.raise_for_status
        return response.text

    @classmethod
    async def get_description(cls, number, doc_type="publication", format="docdb"):
        text = await cls.get_fulltext_result(
            number, doc_type="publication", format="docdb", inquiry="description"
        )
        return Description.model_validate(text)

    @classmethod
    async def get_claims(cls, number, doc_type="publication", format="docdb") -> "Claims":
        text = await cls.get_fulltext_result(
            number, doc_type="publication", format="docdb", inquiry="claims"
        )
        return Claims.model_validate(text)


class PublishedSearchApi:
    @classmethod
    async def search(cls, query, start=1, end=100):
        base_url = "http://ops.epo.org/3.2/rest-services/published-data/search"
        range = f"{start}-{end}"
        logger.debug(f"OPS Search Endpoint - Query: {query}\nRange: {start}-{end}")
        response = await session.get(base_url, params={"Range": range, "q": query})
        if response.status_code == 404:
            return AttrDict.convert(
                {
                    "query": "query",
                    "num_results": 0,
                    "begin": start,
                    "end": end,
                    "results": list(),
                }
            )

        return Search.model_validate(response.text)


class PublishedImagesApi:
    @classmethod
    async def get_images(cls, number, doc_type="publication", format="docdb"):
        base_url = f"http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/{format}/{number}/images"
        response = await session.get(base_url)
        return Images.model_validate(response.text)

    @classmethod
    async def get_page_image(
        cls, country, number, kind, image_type, page_number, image_format="pdf"
    ):
        response = await session.get(
            f"https://ops.epo.org/3.2/rest-services/published-data/images/{country}/{number}/{kind}/{image_type}.{image_format}",
            params={"Range": page_number},
            extensions={"force_cache": True},
        )
        return BytesIO(response.content)

    @classmethod
    async def get_page_image_from_link(cls, link, page_number, image_format="pdf"):
        response = await session.get(
            f"https://ops.epo.org/3.2/rest-services/{link}.{image_format}",
            params={"Range": page_number},
            extensions={"force_cache": True},
        )
        return BytesIO(response.content)


class PublishedApi:
    biblio = PublishedBiblioApi
    fulltext = PublishedFulltextApi
    search = PublishedSearchApi
    images = PublishedImagesApi
