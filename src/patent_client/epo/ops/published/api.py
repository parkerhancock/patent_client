from argparse import ArgumentError
from warnings import warn
import lxml.etree as ET

from patent_client.util import Manager
from patent_client.epo.ops.session import session
from .schema import BiblioResultSchema, SearchSchema, DescriptionSchema, ClaimsSchema

class PublishedDataApi():
    schema = BiblioResultSchema()

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
            constituents = (constituents, )
        url = base_url + ",".join(constituents)
        response = session.get(url)
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        return cls.schema.load(tree)

    @classmethod
    def get_biblio(cls, number, doc_type="publication", format="docdb"):
        return cls.get_constituents(number, doc_type, format, constituents="biblio")
    
    @classmethod
    def get_abstract(cls, number, doc_type="publication", format="docdb"):
        return cls.get_constituents(number, doc_type, format, constituents="abstract")

    @classmethod
    def get_full_cycle(cls, number, doc_type="publication", format="docdb"):
        return cls.get_constituents(number, doc_type, format, constituents="full-cycle")

class PublishedFulltextApi():
    fulltext_jurisdictions = "EP, WO, AT, BE, BG, CA, CH, CY, CZ, DK, EE, ES, FR, GB, GR, HR, IE, IT, LT, LU, MC, MD, ME, NO, PL, PT, RO, RS, SE, SK".split(", ")
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
            raise ArgumentError(f"Fulltext Is Not Available For Country Code {number[:2]}. Fulltext is only available in {', '.join(cls.fulltext_jurisdictions)}")
        response = session.get(url)
        response.raise_for_status
        return response.text

    @classmethod
    def get_description(cls, number, doc_type="publication", format="docdb"):
        text = cls.get_fulltext_result(number, doc_type="publication", format="docdb", inquiry="description")
        tree = ET.fromstring(text.encode())
        return cls.desciption_schema.load(tree)

    @classmethod
    def get_claims(cls, number, doc_type="publication", format="docdb"):
        text = cls.get_fulltext_result(number, doc_type="publication", format="docdb", inquiry="claims")
        tree = ET.fromstring(text.encode())
        return cls.claims_schema.load(tree)

class SearchManager(Manager):
    schema = SearchSchema()
    base_url = "http://ops.epo.org/3.2/rest-services/published-data/search"
    result_size = 100

    def filter(self, *args, **kwargs):
        raise NotImplementedError("This feature doesn't work for this object")

    def _get_search_results_page(self, page=0):
        range = f"{page * self.result_size + 1}-{(page+1)*self.result_size}"
        response = session.get(self.base_url, params={**self.config['filter'], "Range": range})
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        return self.schema.load(tree)

    def _get_search_results_range(self, start=1, end=100):
        range = f"{start}-{end}"
        response = session.get(self.base_url, params={**self.config['filter'], "Range": range})
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        return self.schema.load(tree)

    def __len__(self):
        page = self._get_search_results_range(1, 2)
        offset = self.config['offset'] or 0
        limit = self.config['limit'] or page.num_results - offset
        num_results = page.num_results
        num_results -= offset
        num_results = min(limit, num_results)

        if num_results == 10000:
            warn("Actual Number of Results is Greater Than 10,000 - OPS stops counting after 10,000")
        return num_results

    def _get_results(self):
        num_pages = round(len(self) / self.result_size)
        limit = self.config['limit'] or len(self)
        offset = self.config['offset'] or 0
        max_position = offset + limit

        range = (offset+1, min(offset+self.result_size, max_position))
        while True:
            page = self._get_search_results_range(*range)
            for result in page.results:
                yield result
            if range[1] == max_position:
                break
            range = (range[0] + self.result_size, min(range[1]+self.result_size, max_position))

class PublishedSearchApi():

    @classmethod
    def search(cls, query):
        manager = SearchManager()
        manager.config['filter']['q'] = query
        return manager