import json
import logging
import math
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

import inflection
from patent_client import session
from patent_client.util.base.manager import Manager
from PyPDF2 import PdfFileMerger

from .model import USApplication
from .schema import DocumentSchema
from .schema import USApplicationSchema

logger = logging.getLogger(__name__)


class HttpException(Exception):
    pass


class NotAvailableException(Exception):
    pass


QUERY_FIELDS = "appEarlyPubNumber applId appLocation appType appStatus_txt appConfrNumber appCustNumber appGrpArtNumber appCls appSubCls appEntityStatus_txt patentNumber patentTitle primaryInventor firstNamedApplicant appExamName appExamPrefrdName appAttrDockNumber appPCTNumber appIntlPubNumber wipoEarlyPubNumber pctAppType firstInventorFile appClsSubCls rankAndInventorsList"


class USApplicationManager(Manager[USApplication]):
    primary_key = "appl_id"
    query_url = "https://ped.uspto.gov/api/queries"
    page_size = 20
    __schema__ = USApplicationSchema()

    def __init__(self, *args, **kwargs):
        super(USApplicationManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def __len__(self):
        max_length = self.get_page(0)["numFound"] - self.config.offset
        limit = self.config.limit
        if not limit:
            return max_length
        else:
            return limit if limit < max_length else max_length

    def _get_results(self) -> Iterator[USApplication]:
        num_pages = math.ceil(len(self) / self.page_size)
        page_num = 0
        counter = 0
        while page_num < num_pages:
            page_data = self.get_page(page_num)
            for item in page_data["docs"]:
                if not self.config.limit or counter < self.config.limit:
                    yield self.__schema__.load(item)
                counter += 1
            page_num += 1

    def __iter__(self) -> Iterator[USApplication]:
        return super(USApplicationManager, self).__iter__()

    def get_page(self, page_number):
        if page_number not in self.pages:
            query_params = self.query_params(page_number)
            response = session.post(self.query_url, json=query_params, timeout=10)
            if not response.ok:
                if self.is_online():
                    raise HttpException(
                        f"{response.status_code}\n{response.text}\n{response.headers}\n{json.dumps(query_params)}"
                    )
            data = response.json()
            self.pages[page_number] = data["queryResults"]["searchResponse"]["response"]
        return self.pages[page_number]

    def query_params(self, page_no):
        sort_query = ""
        for s in self.config.order_by:
            if s[0] == "-":
                sort_query += f"{inflection.camelize(s[1:], uppercase_first_letter=False)} desc ".strip()
            else:
                sort_query += (f"{inflection.camelize(s, uppercase_first_letter=False)} asc").strip()
        if not sort_query:
            sort_query = None

        query = list()
        mm_active = True
        for k, v in self.config.filter.items():
            field = inflection.camelize(k, uppercase_first_letter=False)
            if not v:
                continue
            elif type(v) in (list, tuple):
                v = (str(i) for i in v)
                body = " OR ".join(f'"{value}"' if " " in value else value for value in v)
                mm_active = False
            else:
                body = v
            query.append(f"{field}:({body})")

        mm = "100%" if "appEarlyPubNumber" not in query else "90%"

        query = {
            "qf": QUERY_FIELDS,
            "fl": "*",  # ",".join(inflection.camelize(f, uppercase_first_letter=False) for f in RETURN_FIELDS),#"*",
            "fq": list(),
            "searchText": " AND ".join(query).strip(),
            "sort": sort_query,
            "facet": "false",
            "mm": mm,
            "start": page_no * self.page_size + self.config.offset,
            # "rows": self.page_size,
        }
        if not mm_active:
            del query["mm"]
        return query

    @property
    def allowed_filters(self):
        fields = self.fields()
        return list(fields.keys())

    def fields(self):
        """List of fields available to the API"""
        if not hasattr(self.__class__, "_fields"):
            url = "https://ped.uspto.gov/api/search-fields"
            response = session.get(url)
            if not response.ok:
                raise ValueError("Can't get fields!")
            raw = response.json()
            output = {inflection.underscore(key): value for (key, value) in raw.items()}
            self.__class__._fields = output
        return self.__class__._fields

    def is_online(self):
        with session.cache_disabled():
            response = session.get("https://ped.uspto.gov/api/search-fields")
            if response.ok:
                return True
            elif "requested resource is not available" in response.text:
                raise NotAvailableException("Patent Examination Data is Offline - this is a USPTO problem")
            elif "attempt failed or the origin closed the connection" in response.text:
                raise NotAvailableException("The Patent Examination Data API is Broken! - this is a USPTO problem")
            else:
                raise NotAvailableException("There is a USPTO problem")

    @property
    def query_fields(self):
        fields = self.fields()
        for k in sorted(fields.keys()):
            if "facet" in k:
                continue
            print(f"{k} ({fields[k]})")


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class DocumentManager(Manager):
    query_url = "https://ped.uspto.gov/api/queries/cms/public/"
    __schema__ = DocumentSchema()

    def __len__(self):
        url = self.query_url + self.config.filter["appl_id"]
        response = session.get(url)
        response.raise_for_status()
        return len(response.json())

    def _get_results(self) -> Iterator[USApplication]:
        url = self.query_url + self.config.filter["appl_id"]
        response = session.get(url)
        for item in response.json():
            yield self.__schema__.load(item)

    def download(self, docs, path="."):
        if str(path)[-4:].lower() == ".pdf":
            # If we've been given a specific filename, use it
            out_file = Path(path)
        else:
            out_file = Path(path) / "package.pdf"

        files = list()
        try:
            with TemporaryDirectory() as tmpdir:
                for doc in docs:
                    if doc.access_level_category == "PUBLIC":
                        files.append((doc.download(tmpdir), doc))

                out_pdf = PdfFileMerger()
                page = 0
                for f, doc in files:
                    bookmark = f"{doc.mail_room_date} - {doc.code} - {doc.description}"
                    out_pdf.append(str(f), bookmark=bookmark, import_bookmarks=False)
                    page += doc.page_count

                out_pdf.write(str(out_file))
        except (PermissionError, NotADirectoryError):
            # This is needed due to a bug in Windows that prevents cleanup of the tmpdir
            pass
        return out_file
