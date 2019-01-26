import json
import os
import re
import shutil
import time
import xml.etree.ElementTree as ET

import requests
from patent_client import CACHE_BASE
from patent_client import SETTINGS

from .util import Manager, Model, one_to_many, one_to_one

CLIENT_SETTINGS = SETTINGS["ItcEdis"]
if os.environ.get("EDIS_USER", False):
    USERNAME = os.environ["EDIS_USER"]
    PASSWORD = os.environ["EDIS_PASS"]
else:
    USERNAME = CLIENT_SETTINGS["Username"]
    PASSWORD = CLIENT_SETTINGS["Password"]

BASE_URL = "https://edis.usitc.gov/data"
CACHE_DIR = CACHE_BASE / "itc_edis"
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()

# API Guide at: https://www.usitc.gov/docket_services/documents/EDIS3WebServiceGuide.pdf


class ITCInvestigationManager(Manager):
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
            response = session.get(BASE_URL + path, params={"password": PASSWORD})
            import pdb

            pdb.set_trace()
            tree = ET.fromstring(response.text)
            key = tree.find("secretKey").text
            session.auth = (USERNAME, key)

    def filter(self):
        raise NotImplementedError("EDIS Api does not have a search function!")

    def get(self, investigation_number):
        fname = CACHE_DIR / (investigation_number + ".json")
        if fname.exists():
            return ITCInvestigation(json.load(open(fname)))
        else:
            ITCInvestigationManager.authenticate()
            url = self.base_url + investigation_number
            response = session.get(url)
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
            with open(fname, "w") as f:
                json.dump(data, f, indent=2)
            return ITCInvestigation(data)


class ITCInvestigation(Model):
    objects = ITCInvestigationManager()
    documents = one_to_many("patent_client.ITCDocument", investigation_number="number")

    def __repr__(self):
        return f"<ITCInvestigation(number={self.number})>"


class ITCDocumentsManager(Manager):
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
        fname = CACHE_DIR / f"document-{document_id}.json"
        if not fname.exists():
            ITCInvestigationManager.authenticate()
            response = session.get(f"{self.base_url}/{document_id}")
            tree = ET.fromstring(response.text)
            doc_el = tree.find(".//document")
            data = self.parse_doc(doc_el)
            with open(fname, "w") as f:
                json.dump(data, f, indent=2)
        else:
            data = json.load(open(fname))
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

    def get_item(self, key):
        query = {self.allowed_filters[k]: v for (k, v) in self.filter_params.items()}
        page = int(key / 100) + 1
        location = key % 100
        query["pagenumber"] = page
        q_string = re.sub(r'[\{\}":, ]+', "-", json.dumps(query, sort_keys=True)[1:-1])
        fname = CACHE_DIR / f"document-page-{q_string}.json"
        if fname.exists():
            data = json.load(open(fname))
        else:
            ITCInvestigationManager.authenticate()
            response = session.get(self.base_url, params=query)
            tree = ET.fromstring(response.text)[0]
            data = list()
            for element in tree.findall("document"):
                data.append(self.parse_doc(element))
            with open(fname, "w") as f:
                json.dump(data, f, indent=2)
        return ITCDocument(data[location])


class ITCDocument(Model):
    objects = ITCDocumentsManager()
    investigation = one_to_one(
        "patent_client.ITCInvestigation", investigation_number="investigation_number"
    )
    attachments = one_to_many("patent_client.ITCAttachment", document_id="id")

    def __repr__(self):
        return f"<ITCDocument(title={self.title})>"


class ITCAttachmentManager(Manager):
    primary_key = "investigation_number"
    base_url = BASE_URL + "/attachment/"
    allowed_filters = ["document_id"]

    def get_item(self, key):
        doc_id = self.filter_params["document_id"]
        fname = CACHE_DIR / f"attachments-{doc_id}.json"
        if fname.exists() and False:
            data = json.load(open(fname))
        else:
            ITCInvestigationManager.authenticate()
            response = session.get(self.base_url + doc_id)
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
            data = list()
            for element in tree.findall(".//attachment"):
                row = dict()
                for k, value in attribute_dict.items():
                    row[k] = element.find(value).text
                data.append(row)
            with open(fname, "w") as f:
                json.dump(data, f, indent=2)
        return ITCAttachment(data[key])


class ITCAttachment(Model):
    objects = ITCAttachmentManager()
    document = one_to_one("patent_client.ITCDocument", document_id="document_id")

    def __repr__(self):
        return f"<ITCAttachment(title={self.title})>"

    def download(self, path="."):
        *_, ext = self.file_name.split(".")
        filename = f"{self.document.title.strip()} - {self.title}.{ext}"
        cdir = os.path.join(CACHE_DIR, self.document.investigation.number)
        os.makedirs(cdir, exist_ok=True)
        cname = os.path.join(cdir, filename)
        oname = os.path.join(path, filename)
        if not os.path.exists(cname):
            response = session.get(self.download_url, stream=True)
            with open(cname, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        shutil.copy(cname, oname)
