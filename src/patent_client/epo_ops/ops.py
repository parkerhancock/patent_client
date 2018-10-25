import requests
import re
import os
import math
from patent_client import SETTINGS, CACHE_BASE
from lxml import etree as ET
import json
from hashlib import md5
from collections import namedtuple

session = requests.Session()

CLIENT_SETTINGS = SETTINGS["EpoOpenPatentServices"]
if os.environ.get("EPO_KEY", False):
    KEY = os.environ["EPO_KEY"]
    SECRET = os.environ["EPO_SECRET"]
else:
    KEY = CLIENT_SETTINGS["ApiKey"]
    SECRET = CLIENT_SETTINGS["Secret"]
CACHE_DIR = CACHE_BASE / "epo"
CACHE_DIR.mkdir(exist_ok=True)

# XML Namespaces for ElementTree
NS = {
    "ops": "http://ops.epo.org",
    "epo": "http://www.epo.org/exchange",
    "ft": "http://www.epo.org/fulltext",
    "reg": "http://www.epo.org/register",
}

SEARCH_FIELDS = {
    "title": "title",
    "abstract": "abstract",
    "title_and_abstract": "titleandabstract",
    "inventor": "inventor",
    "applicant": "applicant",
    "inventor_or_applicant": "inventorandapplicant",
    "publication": "publicationnumber",
    "epodoc_publication": "spn",
    "application": "applicationnumber",
    "epodoc_application": "sap",
    "priority": "prioritynumber",
    "epodoc_priority": "spr",
    "number": "num",  # Pub, App, or Priority Number
    "publication_date": "publicationdate",  # yyyy, yyyyMM, yyyyMMdd, yyyy-MM, yyyy-MM-dd
    "citation": "citation",
    "cited_in_examination": "ex",
    "cited_in_opposition": "op",
    "cited_by_applicant": "rf",
    "other_citation": "oc",
    "family": "famn",
    "cpc_class": "cpc",
    "ipc_class": "ipc",
    "ipc_core_invention_class": "ci",
    "ipc_core_additional_class": "cn",
    "ipc_advanced_class": "ai",
    "ipc_advanced_additional_class": "an",
    "ipc_advanced_class": "a",
    "ipc_core_class": "c",
    "classification": "cl",  # IPC or CPC Class
    "full_text": "txt",  # title, abstract, inventor and applicant
}

DocDB = namedtuple("DocDB", ["country", "number", "kind", "date", "doc_type"])


class OPSException(Exception):
    pass


class OPSAuthenticationException(OPSException):
    pass


class OpenPatentServicesConnector:
    def authenticate(self, key=None, secret=None):
        auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        global KEY, SECRET
        if key:
            KEY = key
            SECRET = secret

        response = session.post(
            auth_url, auth=(KEY, SECRET), data={"grant_type": "client_credentials"}
        )

        if not response.ok:
            raise OPSAuthenticationException()

        access_token = response.json()["access_token"]
        session.headers["Authorization"] = "Bearer " + access_token

    def pdf_request(self, fname, url, params=dict()):
        if os.path.exists(fname):
            return
        else:
            with open(fname, "wb") as f:
                response = self.request(url, params, stream=True)
                f.write(response.raw.read())

    def request(self, url, params=dict(), stream=False):
        retry = 0
        while retry < 3:
            response = session.get(url, params=params, stream=stream)
            if response.ok:
                return response
            elif response.status_code in (400, 403):
                self.authenticate()
            elif not response.ok:
                tree = ET.fromstring(response.text.encode("utf-8"))
                code = tree.find("./ops:code", NS).text
                message = tree.find("./ops:message", NS).text
                details = tree.find("./ops:details", NS)
                if details is not None:
                    details = "".join(details.itertext())
                else:
                    details = "<None>"
                raise OPSException(
                    f"{response.status_code} - {code} - {message}\nDETAILS: {details} \nURL: {response.request.url}"
                )
            retry += 1
        raise OPSException("Max Retries Exceeded!")

    def xml_request(self, url, params=dict()):
        print(url, params)
        param_hash = md5(json.dumps(params, sort_keys=True).encode("utf-8")).hexdigest()
        fname = os.path.join(
            CACHE_DIR, f"{url[37:].replace('/', '_')}{param_hash if params else ''}.xml"
        )
        if os.path.exists(fname):
            return open(fname).read()
        response = self.request(url, params)
        text = response.text
        with open(fname, "w") as f:
            f.write(text)
        return text

    def original_to_docdb(self, number, doc_type):
        if "PCT" in number:
            return self.parser.pct_to_docdb(number)

        country = country_re.search(number)
        if country:
            country = country.group(0)
            number = number[2:]
        else:
            country = "US"
            number = number

        url = f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/original/{country}.({number})/docdb"
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        output = tree.find("./ops:standardization/ops:output", NS)

        if doc_type == "application":
            app_ref = output.find("./ops:application-reference/epo:document-id", NS)
            return self.parser.docdb_number(app_ref, doc_type)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.parser.docdb_number(pub_ref, doc_type)

    def original_to_epodoc(self, number, doc_type):
        url = f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/original/{number})/epodoc"
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        output = tree.find("./ops:standardization/ops:output", NS)

        if doc_type == "application":
            app_ref = output.find("./ops:application-reference/epo:document-id", NS)
            return self.parser.epodoc_number(app_ref)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.parser.epodoc_number(pub_ref)

    def pct_to_docdb(self, number):
        _, country_year, number = number.split("/")
        country, year = country_year[:2], country_year[2:]
        if len(year) == 2:
            if int(year) > 50:
                year = "19" + year
            else:
                year = "20" + year

        # DocDB format changed in 2004:
        # Pre-2003 - CCyynnnnnW
        # Post-2003 - CCccyynnnnnnW
        if int(year) >= 2004:
            case_number = year + number.rjust(6, "0")
        else:
            case_number = year[2:] + number.rjust(5, "0")
        return DocDB(country, case_number, "W", None, "application")


class InpadocConnector(OpenPatentServicesConnector):
    page_size = 25
    search_url = "http://ops.epo.org/3.2/rest-services/published-data/search"

    def xml_data(self, pub, data_kind):
        case_number = f'{pub.country}.{pub.number}{"." + pub.kind if pub.kind else ""}'
        if data_kind not in (
            "biblio",
            "description",
            "claims",
            "images",
            "legal",
            "family",
        ):
            raise OPSException(data_kind + " is not a valid data kind")
        if data_kind == "legal":
            legal_url = "http://ops.epo.org/3.2/rest-services/legal/{doc_type}/docdb/{case_number}/"
            url = legal_url.format(case_number=case_number, doc_type=pub.doc_type)
        elif data_kind == "family":
            family_url = "http://ops.epo.org/3.2/rest-services/family/{doc_type}/docdb/{case_number}/"
            url = family_url.format(case_number=case_number, doc_type=pub.doc_type)
        else:
            data_url = "http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/docdb/{case_number}/{data_kind}"
            url = data_url.format(
                case_number=case_number, doc_type=pub.doc_type, data_kind=data_kind
            )
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        return tree

    def get_search_page(self, query_dict, page_number):
        start = (page_num - 1) * self.page_size + 1
        end = start + self.page_size - 1
        query = {**self.create_query(query_dict), **{"Range": f"{start}-{end}"}}
        text = self.xml_request(self.search_url, query)
        tree = ET.fromstring(text.encode("utf-8"))
        length = int(tree.find(".//ops:biblio-search", NS).attrib["total-result-count"])
        results = tree.find(".//ops:search-result", NS)
        return [
            self.parse_docdb_number(el.find("./epo:document-id", NS), "publication")
            for el in results
        ]

    def create_query(self, query_dict):
        query = ""
        for keyword, value in query_dict:
            if "values__" in keyword:
                continue
            if len(value.split()) > 1:
                value = f'"{value}"'
            query += SEARCH_FIELDS[keyword] + "=" + value
        return dict(q=query)

    def parse_docdb_number(self, el, doc_type):
        raw_data = {
            "country": el.find("./epo:country", NS),
            "number": el.find("./epo:doc-number", NS),
            "kind": el.find("./epo:kind", NS),
            "date": el.find("./epo:date", NS),
        }
        for k, v in raw_data.items():
            if v is not None:
                raw_data[k] = v.text

        raw_data["doc_type"] = doc_type

        return DocDB(**raw_data)

    def parse_citation(self, el):
        phase = el.attrib["cited-phase"]
        cited_by = el.attrib["cited-by"]
        office = el.attrib.get("office", "")
        pat_cite = el.find("./epo:patcit", NS)
        if pat_cite is not None:
            citation = dict(
                self.docdb_number(
                    pat_cite.find('./epo:document-id[@document-id-type="docdb"]', NS),
                    "publication",
                )._asdict()
            )
        else:
            citation = el.find("./epo:nplcit/epo:text", NS).text
        category = (
            el.find("./epo:category", NS).text
            if el.find("./epo:category", NS) is not None
            else ""
        )
        relevant_claims = el.find("./epo:rel-claims", NS)
        relevant_passages = [
            e.text for e in el.findall("./epo:rel-passage/epo:passage", NS)
        ]
        return {
            "phase": phase,
            "cited_by": cited_by,
            "office": office,
            "citation": citation,
            "category": category,
            "relevant_claims": relevant_claims.text
            if relevant_claims is not None
            else "",
            "relevant_passages": relevant_passages,
        }

    def legal(self, doc_db):
        tree = self.xml_data(doc_db, "legal")
        legal_events = tree.findall(".//ops:legal", NS)
        output = list()
        for le in legal_events:
            row = dict()
            row["description"] = le.attrib["desc"]
            row["explanation"] = le.attrib["infl"]
            row["code"] = le.attrib["code"].strip()
            row["date"] = le.find("./ops:L007EP", NS).text
            output.append(row)
        output = list(sorted(output, key=lambda x: x["date"]))
        return output

    def bib_data(self, doc_db):
        # NOTE: For EP cases with search reports, there is citation data in bib data
        # We just currently are not parsing it
        tree = self.manager.xml_data(doc_db, "biblio")
        documents = tree.findall("./epo:exchange-documents/epo:exchange-document", NS)

        data_items = list()
        for document in documents:
            data = dict()
            data["family_id"] = document.attrib["family-id"]
            bib_data = document.find("./epo:bibliographic-data", NS)

            title = bib_data.find("./epo:invention-title[@lang='en']", NS)
            if title == None:
                title = bib_data.find("./epo:invention-title", NS)
            if title != None:
                data["title"] = title.text.strip()
            else:
                data["title"] = ""
            pub_data = bib_data.find(
                './epo:publication-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            pub_data = self.parse_docdb_number(pub_data, "publication")
            data["doc_db"] = pub_data
            data["publication"] = pub_data.country + pub_data.number + pub_data.kind
            data["publication_date"] = pub_data.date
            data["country"] = pub_data.country

            app_data = bib_data.find(
                './epo:application-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            app_data = dict(self.parse_docdb_number(app_data, "application")._asdict())
            data["application"] = app_data["country"] + app_data["number"]
            data["filing_date"] = app_data.get("date", None)
            original_app_data = bib_data.find(
                './epo:application-reference/epo:document-id[@document-id-type="original"]',
                NS,
            )
            if original_app_data is not None:
                data["original_application_number"] = original_app_data.find(
                    "./epo:doc-number", NS
                ).text

            original_app = bib_data.find(
                './epo:application-reference/epo:document-id[@document-id-type="original"]/epo:doc-number',
                NS,
            )
            if original_app is not None:
                data["original_application_number"] = original_app.text

            intl_class = [
                whitespace_re.sub("", e.text)
                for e in bib_data.findall(
                    "./epo:classifications-ipcr/epo:classification-ipcr/epo:text", NS
                )
            ]
            data["intl_class"] = intl_class

            cpc_classes = bib_data.findall(
                "./epo:patent-classifications/epo:patent-classification", NS
            )
            data["cpc_class"] = [
                self.manager.parser.cpc_class(el) for el in cpc_classes
            ]

            priority_apps = bib_data.findall(
                './epo:priority-claims/epo:priority-claim/epo:document-id[@document-id-type="original"]/epo:doc-number',
                NS,
            )
            data["priority_claims"] = [e.text for e in priority_apps]

            parties = bib_data.find("./epo:parties", NS)
            data["applicants"] = [
                e.text
                for e in parties.findall(
                    './epo:applicants/epo:applicant[@data-format="original"]/epo:applicant-name/epo:name',
                    NS,
                )
            ]
            data["inventors"] = [
                e.text
                for e in parties.findall(
                    './epo:inventors/epo:inventor[@data-format="original"]/epo:inventor-name/epo:name',
                    NS,
                )
            ]
            abstract = document.find('./epo:abstract[@lang="en"]', NS)
            data["abstract"] = (
                "".join(t for t in abstract.itertext()).strip()
                if abstract is not None
                else ""
            )

            refs_cited = bib_data.findall("./epo:references-cited/epo:citation", NS)
            data["references_cited"] = [self.parse_citation(c) for c in refs_cited]
            data_items.append(data)
        return data_items

    def description(self, doc_db):
        tree = self.manager.xml_data(doc_db, "description")
        description = tree.find(
            "./ft:fulltext-documents/ft:fulltext-document/ft:description", NS
        )
        text = "\n".join(description.itertext()).strip()
        return text

    def claims(self, doc_db):
        tree = self.manager.xml_data(doc_db, "claims")
        claims = [
            "".join(e.itertext()).strip()
            for e in tree.findall(
                './ft:fulltext-documents/ft:fulltext-document/ft:claims[@lang="EN"]/ft:claim/ft:claim-text',
                NS,
            )
        ]
        return claims

    def images(self, doc_db):
        if doc_db.doc_type == "application":
            return dict()
        tree = self.manager.xml_data(doc_db, "images")
        images = tree.find(
            './ops:document-inquiry/ops:inquiry-result/ops:document-instance[@desc="FullDocument"]',
            NS,
        )
        data = {
            "url": "http://ops.epo.org/rest-services/" + images.attrib["link"] + ".pdf",
            "num_pages": int(images.attrib["number-of-pages"]),
            "sections": {
                e.attrib["name"]: int(e.attrib["start-page"])
                for e in images.findall("./ops:document-section", NS)
            },
        }
        return data

    def family(self, doc_db):
        tree = self.manager.xml_data(doc_db, "family")
        doc_db_list = list()
        for el in tree.findall("./ops:patent-family/ops:family-member", NS):
            pub_ref = el.find(
                './epo:publication-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            if pub_ref is not None:
                doc_db_list.append(
                    self.manager.parser.docdb_number(pub_ref, "publication")
                )
            else:
                app_ref = el.find(
                    './epo:application-reference/epo:document-id[@document-id-type="docdb"]',
                    NS,
                )
                doc_db_list.append(
                    self.manager.parser.docdb_number(app_ref, "application")
                )
        return doc_db_list
