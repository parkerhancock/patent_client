from patent_client.util.base.manager import Manager
from .session import ExpiredSessionException, session
from .schema import ResultTableSchema
import lxml.etree as ET

class TessManager(Manager):
    result_schema = ResultTableSchema()
    
    def __init__(self, config=None):
        super().__init__(config)
    
    def __len__(self):
        len = self.execute_query()['num_results'] - self.config.offset
        if self.config.limit:
            return min(self.config.limit, len)
        else:
            return len

    def last_updated(self):
        return self.execute_query()['last_updated']

    def _get_results(self):
        # Set up query
        data = self.execute_query()

        # yield records up to limit
        for i, record in enumerate(self.record_iterator(self.config.offset)):
            if i >= self.config.limit:
                break
            yield record

    def record_iterator(self, offset):
        index = offset + 1
        while True:
            try:
                page_response = session.get("https://tmsearch.uspto.gov/bin/jumpto", params={
                    "f": "toc", 
                    "state": self.session.state.string, 
                    "jumpto": index
                })
            except ExpiredSessionException:
                self.execute_query()
                page_response = session.get("https://tmsearch.uspto.gov/bin/jumpto", params={
                    "f": "toc", 
                    "state": session.state.string, 
                    "jumpto": index
                })
            tree = ET.HTML(page_response.text)
            results = self.result_schema(tree)
            for result in results['results']:
                yield result
            index += 100
            if len(results['results'] < 100):
                break
        
    # Prohibited methods
    def order_by(self, *args, **kwargs):
        raise NotImplementedError("The TESS interface does not permit sorting")

    def execute_query(self):
        if "query" in self.config.filter:
            query = self.config.filter['query']
        else:
            query = self.get_query(self.config.filter)
        params = {
            "f": "toc",
            "state": session.state.string,
            "p_search": "search",
            "p_s_All": None,
            "BackReference": None,
            "p_L": "100",
            "p_plural": "yes",
            "p_s_ALL": query,
            "a_search": "Submit Query",
        }
        try:
            response = session.post("https://tmsearch.uspto.gov/bin/gate.exe", data=params)
        except ExpiredSessionException:
            session.login()
            return self.execute_query()
        return self.parse_page(response.text)
        
    def parse_page(self, page):
        tree = ET.HTML(page)
        return self.result_schema.load(tree)
