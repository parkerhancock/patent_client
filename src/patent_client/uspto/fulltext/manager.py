import re
import math
import datetime
from collections import defaultdict
from urllib.parse import urlparse, urljoin

from dateutil.parser import parse as parse_dt

from bs4 import BeautifulSoup as bs, Comment


from patent_client.util import Manager

from .schema import PublicationSchema
from .parser import FullTextParser
from .session import session

def standardize_date(input):
    if isinstance(input, datetime.date):
        return input.strftime("%Y%m%d")
    elif isinstance(input, datetime.datetime):
        return input.date().strftime("%Y%m%d")
    else:
        return parse_dt(input).date().strftime("%Y%m%d")
    
clean_text = lambda string: re.sub(r"\s+", " ", string).strip()
clean_number = lambda string: re.sub(r"[^DREP\d]", "", string).strip()

class FullTextManager(Manager):
    __schema__ = PublicationSchema
    search_fields = None
    search_params = None
    search_url = None
    pub_base_url = None
    result_model = None

    def __init__(self, *args, **kwargs):
        super(FullTextManager, self).__init__(*args, **kwargs)
        self.query = self.generate_query(self.config['filter'])
        self.pages = dict()

    def __len__(self):
        self.get_page(0)
        return self.num_results

    def _get_results(self):
        limit = self.config['limit']
        offset = self.config['offset'] or 0
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
                    
    def generate_query(self, query):
        if "query" in query:
            return query['query'][0]
        query_segments = list()
        date_queries = defaultdict(dict)
        
        def handle_query_segment(k, v):
            if "date" in k:
                kind, *q_type = k.split("_date")
                kind += "_date"
                q_type = q_type[0].strip("_")
                if not q_type:
                    if "->" in v: # Allow for arrow ranges
                        v = v.split("->")
                        q_type = "range"
                    else:
                        q_type = "exact"
                date_queries[kind][q_type] = v
            else:
                if k not in self.search_fields: raise ValueError(f"{k} is not a supported search field!")
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
            if k not in self.search_fields: raise ValueError(f"{k} is not a supported search field!")
            if "exact" in v:
                query_segments.append(f"{self.search_fields[k]}/{standardize_date(v['exact'])}")
            elif "range" in v:
                r = tuple(standardize_date(d) for d in v['range'])
                query_segments.append(f"{self.search_fields[k]}/{r[0]}->{r[1]}")
            elif "gt" or "lt" in v:
                gt = standardize_date(v.get("gt", standardize_date("19000101")))
                lt = standardize_date(v.get("lt", datetime.datetime.now().date().strftime("%Y%m%d")))
                query_segments.append(f"{self.search_fields[k]}/{gt}->{lt}")

        return " AND ".join(query_segments)

    def get_page(self, page_no):
        """pages here are zero-indexed, which means they have to
        be incremented by one before the request"""
        if page_no in self.pages:
            return self.pages[page_no]
        params = {**self.search_params, **dict(Query=self.query)}
        params["p"] = str(page_no + 1)
        response = session.get(self.search_url, params=params)
        if response.text.startswith("Error"):
            raise ValueError("The USPTO Search Interface threw an error!")
        response.raise_for_status()
        response_text = response.text
        results = self.parse_page(response_text)
        self.pages[page_no] = results
        return results

    def parse_page(self, response_text):
        if ("No patents have matched your query" in response_text
            or "No application publications have matched your query" in response_text):
            self.num_results = 0
            return list()
        soup = bs(response_text, "lxml")
        self.num_results = int(soup.find_all("i")[1].find_all("strong")[-1].text)
        try:
            results = soup.find_all("table")[1].find_all("tr")[1:]
            return [
                self.result_model(
                    publication_number=clean_number(r.find_all("td")[1].text),
                    title=clean_text(r.find_all("td")[3].text),) for r in results
            ]
             
        except IndexError: # Publications and Patents are formatted slightly differently:
            results = soup.find_all("table")[0].find_all("tr")[1:]
            return [
                self.result_model(
                    publication_number=clean_number(r.find_all("td")[1].text),
                    title=clean_text(r.find_all("td")[2].text),) for r in results
            ]


    def get(self, *args, **kwargs):
        # Short-circuit this method to fetch a specific patent if only publication_number is passed
        if len(args) == 1 or (len(kwargs) == 1 and "publication_number" in kwargs):
            publication_number = args[0] if args else kwargs['publication_number']
            url = self.pub_base_url.format(publication_number=publication_number)
            response = session.get(url)
            response.raise_for_status()
            parsed = FullTextParser().parse(response.text)
            return self.__schema__().deserialize(parsed)
        else:
            return super(FullTextManager, self).get(*args, **kwargs)

class ImageManager(Manager):
    def get(self, publication_number):
        query = {"PageNum": 0, "docid": publication_number, "IDKey": None}
        response = session.get(self.BASE_URL, params=query)
        response.raise_for_status()
        soup = bs(response.text, 'lxml')
        return self.__schema__().deserialize({
            "publication_number": publication_number,
            "pdf_url": self.get_pdf_url(soup),
            "sections": self.get_section_data(soup)
        })


    def get_pdf_url(self, page_soup):
        pdf_path_string = page_soup.find("embed", attrs={"type": "application/pdf"})['src']
        # Get and edit path
        pdf_path = urlparse(pdf_path_string).path
        base, _ = pdf_path.rsplit('/', 1)
        pdf_path = "/".join((base, '0.pdf'))
        # Generate final url
        pdf_url = urljoin(self.BASE_URL, pdf_path)
        return pdf_url

    def get_page_data(self, section_url):
        response = session.get(section_url)
        response.raise_for_status()
        page_soup = bs(response.text, "lxml")
        # Get last two top-level comments
        page_data = page_soup.find_all(string=lambda x: isinstance(x, Comment), recursive=False)[-2:]
        # They're in the format of "PageNum=#" and "NumPages=#". So we convert to dictionary
        data = (i.strip().split("=") for i in page_data)
        data_dict = {d[0]: int(d[1]) for d in data}
        return data_dict

    def get_section_data(self, page_soup):
        section_tags = [i.find_parent("a") for i in page_soup.find_all("img", src="/templates/redball.gif")]
        links = {i.text.strip(): urljoin(self.BASE_URL, i['href']) for i in section_tags}
        data = [{"name": section_name, **self.get_page_data(section_url)} for section_name, section_url in links.items()]
        # Calculate Page Breaks
        total_pages = data[0]['NumPages']
        section_starts = [d['PageNum'] for d in data]
        section_ends = [p-1 for p in section_starts[1:]] + [total_pages,]
        sections = list(zip(section_starts, section_ends))
        section_names = [d['name'] for d in data]
        result = dict(zip(section_names, sections))
        return result




        




    



        