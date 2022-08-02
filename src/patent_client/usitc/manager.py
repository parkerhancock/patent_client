from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET

from patent_client.util import Manager

from .schema import ITCAttachmentSchema
from .schema import ITCDocumentSchema
from .schema import ITCInvestigationSchema
from .session import session

BASE_URL = "https://edis.usitc.gov/data"


class ITCInvestigationManager(Manager["ITCInvestigation"]):
    base_url = BASE_URL + "/investigation/"

    def _get_results(self):
        raise NotImplementedError("EDIS API does not have a search function!")

    def get(self, investigation_number):
        url = self.base_url + investigation_number
        response = session.get(url)
        return ITCInvestigationSchema().load(response.text)


class ITCDocumentManager(Manager["ITCDocument"]):
    primary_key = "document_id"
    base_url = BASE_URL + "/document"
    allowed_filters = {
        "investigation_number": "investigationNumber",
        "phase": "investigationPhase",
        "type": "documentType",
        "firm": "firmOrg",
        "security": "securityLevel",
        "document_id": "document_id",
    }

    def get_document_by_id(self, document_id):
        breakpoint()
        response = session.get(f"{self.base_url}/{document_id}")
        tree = ET.fromstring(response.text)
        doc_el = tree.find(".//document")
        return ITCDocumentSchema().load(doc_el)

    def _get_results(self):
        if "document_id" in self.config["filter"]:
            yield self.get_document_by_id(self.config["document_id"])
        else:
            query = {self.allowed_filters[k]: v for (k, v) in self.config["filter"].items()}
            page = 1
            page_length = None
            while not page_length or page_length >= 100:
                query["pagenumber"] = page
                q_string = re.sub(r'[\{\}":, ]+', "-", json.dumps(query, sort_keys=True)[1:-1])
                response = session.get(self.base_url, params=query)
                tree = ET.fromstring(response.text)[0]
                page_length = len(tree.findall("document"))
                for doc in tree.findall("document"):
                    yield ITCDocumentSchema().load(doc)
                page += 1


class ITCAttachmentManager(Manager["ITCAttachment"]):
    primary_key = "id"
    base_url = BASE_URL + "/attachment/"
    allowed_filters = ["document_id"]

    def _get_results(self):
        doc_id = self.config["filter"]["document_id"]
        response = session.get(self.base_url + doc_id)
        tree = ET.fromstring(response.text)
        for element in tree.findall(".//attachment"):
            yield ITCAttachmentSchema().load(element)
