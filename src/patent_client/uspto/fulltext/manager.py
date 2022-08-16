import datetime
import logging
import math
import re
import time
from collections import defaultdict


import lxml.etree as ET
from dateutil.parser import parse as parse_dt
from patent_client.util import Manager
from patent_client.util.base.collections import ListManager

from .schema.images import ImageHtmlSchema
from .schema.images import ImageSchema
from .session import session

logger = logging.getLogger(__name__)


def rate_limit(func, delay=0.001):
    last_call = time.time()

    def limited_func(*args, **kwargs):
        wait = delay - (time.time() - last_call)  # noqa: F823
        if wait > 0:
            time.sleep(wait)
        last_call = time.time()
        func(*args, **kwargs)

    return limited_func


def standardize_date(input):
    if isinstance(input, datetime.date):
        date = input
    elif isinstance(input, datetime.datetime):
        date = input.date()
    else:
        date = parse_dt(input).date()
    return f"{date.month}/{date.day}/{date.year}"


clean_text = lambda string: re.sub(r"\s+", " ", string).strip()
clean_number = lambda string: re.sub(r"[^DREP\d]", "", string).strip()


class FullTextManager(Manager):
    __schema__ = None
    search_fields = None
    search_params = None
    search_url = None
    pub_base_url = None
    result_model = None
    result_page_parser = None

    def __init__(self, *args, **kwargs):
        super(FullTextManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def __len__(self):
        self.get_page(0)
        return self.num_results

    def _get_results(self):
        limit = self.config.limit
        offset = self.config.offset or 0
        starting_page = int(offset / 50)
        starting_offset = offset - starting_page * 50
        num_pages = math.ceil(len(self) / 50)
        items_returned = 0
        offset_counter = 0
        for page_num in range(starting_page, num_pages):
            page_results = self.get_page(page_num)
            for item in page_results:
                if offset_counter < starting_offset:
                    offset_counter += 1
                    continue
                items_returned += 1
                if limit and items_returned > limit:
                    return
                yield item

    @property
    def query(self):
        return self.generate_query(self.config.filter)

    def generate_query(self, query):
        if "query" in query:
            return query["query"]
        query_segments = list()
        date_queries = defaultdict(dict)

        def handle_query_segment(k, v):
            if "date" in k:
                kind, *q_type = k.split("_date")
                kind += "_date"
                q_type = q_type[0].strip("_")
                if not q_type:
                    if "->" in v:  # Allow for arrow ranges
                        v = v.split("->")
                        q_type = "range"
                    else:
                        q_type = "exact"
                date_queries[kind][q_type] = v
            else:
                if k not in self.search_fields:
                    raise ValueError(f"{k} is not a supported search field!")
                if " " in v:
                    v = f'"{v}"'
                query_segments.append(f"{self.search_fields[k]}/{v}")

        # Create normal queries, and divert date queries for separate processing
        for k, v in query.items():
            if isinstance(v, list):
                for i in v:
                    handle_query_segment(k, i)
            else:
                handle_query_segment(k, v)

        # Handle Date Queries
        for k, v in date_queries.items():
            if k not in self.search_fields:
                raise ValueError(f"{k} is not a supported search field!")
            if "exact" in v:
                query_segments.append(f"{self.search_fields[k]}/{standardize_date(v['exact'])}")
            elif "range" in v:
                r = tuple(standardize_date(d) for d in v["range"])
                query_segments.append(f"{self.search_fields[k]}/{r[0]}->{r[1]}")
            elif "gt" or "lt" in v:
                gt = standardize_date(v.get("gt", standardize_date("19000101")))
                lt = standardize_date(v.get("lt", datetime.datetime.now().date().strftime("%Y%m%d")))
                query_segments.append(f"{self.search_fields[k]}/{gt}->{lt}")

        query = " AND ".join(query_segments)
        logging.debug(f"FullText Manager Generated Query: {query}")
        return query

    def get_page(self, page_no):
        """pages here are zero-indexed, which means they have to
        be incremented by one before the request"""
        if page_no in self.pages:
            return self.pages[page_no]
        params = {**self.search_params, **dict(Query=self.query)}
        params["p"] = str(page_no + 1)
        response = session.get(self.search_url, params=params)
        if response.text.startswith("Error"):
            if response.from_cache:
                session.cache.delete(response.cache_key)
            raise ValueError(f"The USPTO Search Interface threw an error!\n{response.request.url}\n{response.text}")

        response.raise_for_status()
        response_text = response.text
        results = self.parse_page(response_text)
        self.pages[page_no] = results
        return results

    def parse_page(self, response_text):
        if (
            "No patents have matched your query" in response_text
            or "No application publications have matched your query" in response_text
        ):
            self.num_results = 0
            return list()

        tree = ET.HTML(response_text)
        search_box = tree.xpath('.//form[@name="refine"]|.//input[@name="Refine"]')
        if not search_box:
            # The query resulted in a single match, which redirected to the document
            result = self.__schema__.load(tree)
            result_stub = self.result_model(seq=1, publication_number=result.publication_number, title=result.title)
            self.num_results = 1
            return ListManager([result_stub,])

        result = self.result_page_parser.load(tree)
        self.num_results = result.num_results
        return result.results

    def get(self, *args, **kwargs):
        # Short-circuit this method to fetch a specific patent if only publication_number is passed
        if len(args) == 1 or (len(kwargs) == 1 and "publication_number" in kwargs):
            publication_number = args[0] if args else kwargs["publication_number"]
            url = self.pub_base_url.format(publication_number=publication_number)
            response = session.get(url)
            response.raise_for_status()
            return self.__schema__.load(response.text)
        else:
            return super(FullTextManager, self).get(*args, **kwargs)


class ImageManager(Manager):
    __schema__ = ImageSchema()
    html_schema = ImageHtmlSchema()

    def get(self, pdf_url):
        full_doc = self.get_image_data(pdf_url)
        full_doc.pdf_url = self.DL_URL.format(pdf_id=full_doc.pdf_url_id)
        full_doc["sections"] = [
            {"name": name, **self.get_image_data(self.BASE_URL + url)} for name, url in full_doc.sections.items()
        ]
        last_page = full_doc.num_pages
        for section in reversed(full_doc.sections):
            section["end_page"] = last_page
            last_page = section["start_page"] - 1
        return self.__schema__.load(full_doc)

    def get_image_data(self, url, params=dict()):
        response = session.get(url, params=params)
        response.raise_for_status()
        if not response.text:
            return dict()
        data = self.html_schema.load(response.text)
        return data
