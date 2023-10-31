import json
import logging
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import AsyncIterator

import inflection
from patent_client.util.asyncio_util import run_sync
from patent_client.util.base.manager import Manager
from patent_client.util.request_util import get_start_and_row_count
from PyPDF2 import PdfFileMerger

from .api import PatentExaminationDataSystemApi
from .model import USApplication
from .schema import DocumentSchema
from .schema import USApplicationSchema
from .session import session


logger = logging.getLogger(__name__)


class HttpException(Exception):
    pass


class USApplicationManager(Manager[USApplication]):
    primary_key = "appl_id"
    query_url = "https://ped.uspto.gov/api/queries"
    page_size = 20
    __schema__ = USApplicationSchema()

    def __init__(self, *args, **kwargs):
        super(USApplicationManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    async def alen(self):
        api = PatentExaminationDataSystemApi()
        max_length = (await api.create_query(**self.get_query_params())).num_found
        return min(max_length, self.config.limit) if self.config.limit else max_length

    async def _aget_results(self) -> AsyncIterator[USApplication]:
        query_params = self.get_query_params()
        api = PatentExaminationDataSystemApi()
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            page = await api.create_query(**{**query_params, "start": start, "rows": rows})
            for app in page.applications:
                yield app
            if len(page.applications) < rows:
                break

    def get_query_params(self):
        if "query" in self.config.filter:
            query_text = self.config.filter["query"]
        else:
            query = list()
            for k, v in self.config.filter.items():
                field = inflection.camelize(k, uppercase_first_letter=False)
                if not v:
                    continue
                elif type(v) in (list, tuple):
                    v = (str(i) for i in v)
                    body = " OR ".join(f'"{value}"' if " " in value else value for value in v)
                else:
                    body = v
                query.append(f"{field}:({body})")
            query_text = " AND ".join(query).strip()
        if self.config.order_by:
            sort_query = ""
            for s in self.config.order_by:
                if s[0] == "-":
                    sort_query += f"{inflection.camelize(s[1:], uppercase_first_letter=False)} desc ".strip()
                else:
                    sort_query += (f"{inflection.camelize(s, uppercase_first_letter=False)} asc").strip()
        else:
            sort_query = None

        mm = "0%" if "appEarlyPubNumber" not in query else "90%"

        query_data = {
            "query": query_text,
            "facet": False,
            "minimum_match": mm,
        }
        if sort_query:
            query_data["sort"] = sort_query
        return query_data

    @property
    def allowed_filters(self):
        fields = self.fields()
        return list(fields.keys())

    def fields(self):
        """List of fields available to the API"""
        if not hasattr(self.__class__, "_fields"):
            url = "https://ped.uspto.gov/api/search-fields"
            response = run_sync(session.get(url))
            if not response.status_code == 200:
                raise ValueError("Can't get fields!")
            raw = response.json()
            output = {inflection.underscore(key): value for (key, value) in raw.items()}
            self.__class__._fields = output
        return self.__class__._fields

    def is_online(self):
        return run_sync(PatentExaminationDataSystemApi.is_online)

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

    async def alen(self):
        url = self.query_url + self.config.filter["appl_id"]
        response = await session.get(url)
        response.raise_for_status()
        return len(response.json())

    async def _aget_results(self) -> AsyncIterator[USApplication]:
        url = self.query_url + self.config.filter["appl_id"]
        response = await session.get(url)
        for item in response.json():
            yield self.__schema__.load(item)

    def download(self, docs, path="."):
        run_sync(self.adownload(docs, path))

    async def adownload(self, docs, path="."):
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
                        files.append((await doc.adownload(tmpdir), doc))

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
