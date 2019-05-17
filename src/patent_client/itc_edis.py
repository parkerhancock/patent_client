import json
import os
import re
import shutil
import time
import xml.etree.ElementTree as ET

import requests

from patent_client import SETTINGS
from patent_client import session

from .util import IterableManager, Model, one_to_many, one_to_one

CLIENT_SETTINGS = SETTINGS["ItcEdis"]
if os.environ.get("EDIS_USER", False):
    USERNAME = os.environ["EDIS_USER"]
    PASSWORD = os.environ["EDIS_PASS"]
else:
    USERNAME = CLIENT_SETTINGS["Username"]
    PASSWORD = CLIENT_SETTINGS["Password"]

BASE_URL = "https://edis.usitc.gov/data"

# API Guide at: https://www.usitc.gov/docket_services/documents/EDIS3WebServiceGuide.pdf

SECRET_KEY = None

class AuthenticationException(Exception):
    pass

class ITCInvestigationManager(IterableManager):
    max_retries = 3
    auth_time = 10 * 60  # Re-authenticate every # seconds
    last_auth = 0
    base_url = BASE_URL + "/investigation/"

    def authenticate():
        if (
            time.time() - ITCInvestigationManager.last_auth
            > ITCInvestigationManager.auth_time
        ):
            path = "/secretKey/" + USERNAME
            with session.cache_disabled():
                response = session.get(BASE_URL + path, params={"password": PASSWORD})
            if not response.ok:
                import pdb; pdb.set_trace()
                raise AuthenticationException("EDIS Authentication Failed! Did you provide the correct username and password?")
            tree = ET.fromstring(response.text)
            SECRET_KEY = tree.find("secretKey").text

    def filter(self):
        raise NotImplementedError("EDIS Api does not have a search function!")

    def get(self, investigation_number):
        ITCInvestigationManager.authenticate()
        url = self.base_url + investigation_number
        response = session.get(url, auth=(USERNAME, SECRET_KEY))
        tree = ET.fromstring(response.text)
        tree = tree[0][0]
        data = {
            "phase": tree.find("investigationPhase").text,
            "number": tree.find("investigationNumber").text,
            "status": tree.find("investigationStatus").text,
            "title": tree.find("investigationTitle").text,
            "type": tree.find("investigationType").text,
            "doc_list_url": tree.find("documentListUri").text,
            "docket_number": tree.find("docketNumber").text,
        }
        return ITCInvestigation(data)


class ITCInvestigation(Model):
    objects = ITCInvestigationManager()
    documents = one_to_many("patent_client.ITCDocument", investigation_number="number")

    def __repr__(self):
        return f"<ITCInvestigation(number={self.number})>"


class ITCDocumentsManager(IterableManager):
    primary_key = "investigation_number"
    base_url = BASE_URL + "/document"
    allowed_filters = {
        "investigation_number": "investigationNumber",
        "phase": "investigationPhase",
        "type": "documentType",
        "firm": "firmOrg",
        "security": "securityLevel",
    }

    def get(self, document_id):
        ITCInvestigationManager.authenticate()
        response = session.get(f"{self.base_url}/{document_id}", auth=(USERNAME, SECRET_KEY))
        tree = ET.fromstring(response.text)
        doc_el = tree.find(".//document")
        data = self.parse_doc(doc_el)
        return ITCDocument(data)

    def parse_doc(self, element):
        attribute_dict = dict(
            type="documentType",
            title="documentTitle",
            investigation_number="investigationNumber",
            security="securityLevel",
            filing_org="firmOrganization",
            filed_by="filedBy",
            filed_on_behalf_of="onBehalfOf",
            action_jacket_control_number="actionJacketControlNumber",
            memorandum_control_number="memorandumControlNumber",
            attachment_url="attachmentListUri",
            date="documentDate",
            last_modified="modifiedDate",
            id="id",
        )
        data = dict()
        for key, value in attribute_dict.items():
            data[key] = element.find(value).text
        return data

    def __iter__(self):
        query = {self.allowed_filters[k]: v for (k, v) in self.config['filter'].items()}
        page = 1
        page_length = None
        while not page_length or page_length >= 100:
            query["pagenumber"] = page
            q_string = re.sub(r'[\{\}":, ]+', "-", json.dumps(query, sort_keys=True)[1:-1])
            ITCInvestigationManager.authenticate()
            response = session.get(self.base_url, params=query, auth=(USERNAME, SECRET_KEY))
            tree = ET.fromstring(response.text)[0]
            page_length = len(tree.findall("document"))
            docs = map(self.parse_doc, tree.findall("document"))
            for doc in docs:
                yield ITCDocument(doc)
            page += 1


class ITCDocument(Model):
    objects = ITCDocumentsManager()
    investigation = one_to_one(
        "patent_client.ITCInvestigation", investigation_number="investigation_number"
    )
    attachments = one_to_many("patent_client.ITCAttachment", document_id="id")

    def __repr__(self):
        return f"<ITCDocument(title={self.title})>"


class ITCAttachmentManager(IterableManager):
    primary_key = "investigation_number"
    base_url = BASE_URL + "/attachment/"
    allowed_filters = ["document_id"]

    def __iter__(self):
        doc_id = self.config['filter']["document_id"]
        ITCInvestigationManager.authenticate()
        response = session.get(self.base_url + doc_id, auth=(USERNAME, SECRET_KEY))
        tree = ET.fromstring(response.text)
        attribute_dict = dict(
            id="id",
            document_id="documentId",
            title="title",
            size="fileSize",
            file_name="originalFileName",
            pages="pageCount",
            created_date="createDate",
            last_modified_date="lastModifiedDate",
            download_url="downloadUri",
        )
        for element in tree.findall(".//attachment"):
            row = dict()
            for k, value in attribute_dict.items():
                row[k] = element.find(value).text
            yield ITCAttachment(row)


class ITCAttachment(Model):
    objects = ITCAttachmentManager()
    document = one_to_one("patent_client.ITCDocument", document_id="document_id")

    def __repr__(self):
        return f"<ITCAttachment(title={self.title})>"

    def download(self, path="."):
        *_, ext = self.file_name.split(".")
        filename = f"{self.document.title.strip()} - {self.title}.{ext}"
        oname = os.path.join(path, filename)
        if not os.path.exists(oname):
            response = session.get(self.download_url, auth=(USERNAME, SECRET_KEY), stream=True)
            with open(oname, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        return oname
