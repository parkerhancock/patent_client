import re
from urllib.parse import urljoin

import lxml.etree as ET

from patent_client._async.http_client import PatentClientSession

from .model import DocumentList, GlobalDossier

client = PatentClientSession(
    headers={
        "Authorization": "OQmPwAN1QD4OXe25jpmMD27zmnM21gIL0lg85G6j",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/21.1.1.164 Safari/602.1.507",
    }
)


class GlobalDossierApi:
    def __init__(self):
        self.api_base_url = None

    async def get_base_url(self):
        if self.api_base_url:
            return self.api_base_url
        base_url = "https://globaldossier.uspto.gov"
        response = await client.get(base_url)
        tree = ET.HTML(response.text)
        scripts = [urljoin(base_url, x) for x in tree.xpath("//script/@src")]
        main_script = next(filter(lambda x: "main" in x, scripts))
        response = await client.get(main_script)
        api_url_re = re.compile(r'apiURL:\s*"([^"]+)"')
        match = api_url_re.search(response.text)
        self.api_base_url = match.group(1) if match else None
        return self.api_base_url

    async def get_file(self, doc_number, type_code="application", office_code="US"):
        url = f"{await self.get_base_url()}/patent-family/svc/family/{type_code}/{office_code}/{doc_number}"
        _ = await client.options(url)
        response = await client.get(url)
        response.raise_for_status()
        return GlobalDossier.model_validate_json(response.content)

    async def get_doc_list(self, country, doc_number, kind_code):
        url = f"{await self.get_base_url()}/doc-list/svc/doclist/{country}/{doc_number}/{kind_code}"
        response = await client.get(url)
        response.raise_for_status()
        return DocumentList.model_validate_json(response.content)

    async def get_document(self, country, doc_number, document_id, out_path):
        url = f"{await self.get_base_url()}/doc-content/svc/doccontent/{country}/{doc_number}/{document_id}/1/PDF"
        return await client.download(url, path=out_path)
