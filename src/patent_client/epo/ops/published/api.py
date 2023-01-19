import logging
from io import BytesIO

from patent_client.epo.ops.session import session
from yankee.data import AttrDict


logger = logging.getLogger(__name__)


class PublishedBiblioApi:
    @classmethod
    def get_constituents(cls, number, doc_type="publication", format="docdb", constituents=("biblio",)):
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
        return response.text

    @classmethod
    def get_biblio(cls, number, doc_type="publication", format="docdb"):
        return cls.get_constituents(number, doc_type, format, constituents="biblio")

    @classmethod
    def get_abstract(cls, number, doc_type="publication", format="docdb"):
        return cls.get_constituents(number, doc_type, format, constituents="abstract")

    @classmethod
    def get_full_cycle(cls, number, doc_type="publication", format="docdb"):
        return cls.get_constituents(number, doc_type, format, constituents="full-cycle")


class PublishedFulltextApi:
    fulltext_jurisdictions = "EP, WO, AT, BE, BG, CA, CH, CY, CZ, DK, EE, ES, FR, GB, GR, HR, IE, IT, LT, LU, MC, MD, ME, NO, PL, PT, RO, RS, SE, SK".split(
        ", "
    )

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
    def get_description(cls, number, doc_type="publication", format="docdb"):
        return cls.get_fulltext_result(number, doc_type="publication", format="docdb", inquiry="description")

    @classmethod
    def get_claims(cls, number, doc_type="publication", format="docdb"):
        return cls.get_fulltext_result(number, doc_type="publication", format="docdb", inquiry="claims")


class PublishedSearchApi:
    @classmethod
    def search(cls, query, start=1, end=100):
        base_url = "http://ops.epo.org/3.2/rest-services/published-data/search"
        range = f"{start}-{end}"
        logger.debug(f"OPS Search Endpoint - Query: {query}\nRange: {start}-{end}")
        response = session.get(base_url, params={"Range": range, "q": query})
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
        response.raise_for_status()
        return response.text


class PublishedImagesApi:
    @classmethod
    def get_images(cls, number, doc_type="publication", format="docdb"):
        base_url = f"http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/{format}/{number}/images"
        response = session.get(base_url)
        response.raise_for_status()
        return response.text

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
    search = PublishedSearchApi
    images = PublishedImagesApi
