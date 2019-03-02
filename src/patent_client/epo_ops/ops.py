import json
import math
import os
import re
from collections import namedtuple
from hashlib import md5

import requests
from lxml import etree as ET
from patent_client import SETTINGS
from patent_client.epo_ops import CACHE_DIR, TEST_DIR

session = requests.Session()

CLIENT_SETTINGS = SETTINGS["EpoOpenPatentServices"]
if os.environ.get("EPO_KEY", False):
    KEY = os.environ["EPO_KEY"]
    SECRET = os.environ["EPO_SECRET"]
else:
    KEY = CLIENT_SETTINGS["ApiKey"]
    SECRET = CLIENT_SETTINGS["Secret"]

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
    "ipc_core_class": "c",
    "classification": "cl",  # IPC or CPC Class
    "full_text": "txt",  # title, abstract, inventor and applicant
}

EpoDoc = namedtuple("EpoDoc", ["number", "kind", "date", "doc_type"])
DocDB = namedtuple("DocDB", ["country", "number", "kind", "date", "doc_type", "family_id"])
whitespace_re = re.compile(" +")
country_re = re.compile(r"^[A-Z]{2}")
ep_case_re = re.compile(r"EP(?P<number>[\d]+)(?P<kind>[A-Z]\d)?")
Claim = namedtuple("Claim", ["number", "text", "limitations"])
cn_re = re.compile(r"^\d+")
lim_re = re.compile(r"([:;])")


def clean_claims(claims):
    def parse_claim(limitations, counter):
        preamble = limitations[0]
        claim_number = counter
        if preamble[0].isupper():
            limitations = [f"{str(claim_number)}. {preamble}", *limitations[1:]]
            counter += 1
        elif cn_re.search(preamble):
            claim_number = int(cn_re.search(preamble).group(0))
            counter = claim_number + 1

        # Fix trailing "ands" in the claim language
        clean_limitations = list()
        for i, lim in enumerate(limitations):
            try:
                if limitations[i + 1].split()[0].lower() == "and":
                    lim = lim + " and"
                    limitations[i + 1] = " ".join(limitations[i + 1].split()[1:])
            except IndexError:
                pass
            clean_limitations.append(lim.strip())
        return (
            Claim(
                number=claim_number,
                text="\n".join(clean_limitations),
                limitations=clean_limitations,
            ),
            counter,
        )

    if len(claims) > 1:
        counter = 1
        claim_list = list()
        for claim in claims:
            segments = iter(lim_re.split(claim))
            limitations = list()
            while True:
                try:
                    phrase = next(segments)
                    delimiter = next(segments)
                    limitations.append(phrase + delimiter)
                except StopIteration:
                    limitations.append(phrase)
                    break
            claim, counter = parse_claim(limitations, counter)
            claim_list.append(claim)
        return claim_list

    lines = claims[0].split("\n")

    preambles = ["i claim", "we claim", "what is claimed", "claims"]
    c_preambles = ["a", "an", "the"]

    if any(pa in lines[0].lower().replace(" ", "") for pa in preambles):
        lines = lines[1:]

    new_lines = list()

    for line in lines:
        segments = re.split(r"(?<=[^\d]\.) ", line)
        new_lines += segments

    claims = list()
    counter = 1
    limitations = list()
    while new_lines:
        line = new_lines.pop(0)
        if limitations and (
            any(cp in line[0].split()[0].lower() for cp in c_preambles)
            or cn_re.search(line)
            or not new_lines
        ):
            claim, counter = parse_claim(limitations, counter)
            claims.append(claim)
            limitations = [line]
        else:
            limitations.append(line)

    claim, counter = parse_claim(limitations, counter)
    claims.append(claim)
    return claims


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
        param_hash = md5(json.dumps(params, sort_keys=True).encode("utf-8")).hexdigest()
        if self.test_mode:
            fname = os.path.join(
                TEST_DIR, f"{url[37:].replace('/', '_')}{param_hash if params else ''}.xml"
            )

        else:
            fname = os.path.join(
                CACHE_DIR, f"{url[37:].replace('/', '_')}{param_hash if params else ''}.xml"
            )
        print(fname)
        if os.path.exists(fname):
            return open(fname, encoding="utf-8").read()
        response = self.request(url, params)
        text = response.text
        with open(fname, "w", encoding="utf-8") as f:
            f.write(text)
        return text

    def original_to_docdb(self, number, doc_type):
        if "PCT" in number:
            return self.pct_to_docdb(number)
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
            return self.docdb_number(app_ref, doc_type)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.docdb_number(pub_ref, doc_type)

    def original_to_epodoc(self, number, doc_type):
        url = f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/original/{number})/epodoc"
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        output = tree.find("./ops:standardization/ops:output", NS)

        if doc_type == "application":
            app_ref = output.find("./ops:application-reference/epo:document-id", NS)
            return self.epodoc_number(app_ref, doc_type)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.epodoc_number(pub_ref, doc_type)

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
        return DocDB(country, case_number, "W", None, "application", None)

    def docdb_number(self, el, doc_type):
        raw_data = {
            "country": el.find("./epo:country", NS),
            "number": el.find("./epo:doc-number", NS),
            "kind": el.find("./epo:kind", NS),
            "date": el.find(".//epo:date", NS),
        }
        for k, v in raw_data.items():
            if v is not None:
                raw_data[k] = v.text

        raw_data["doc_type"] = doc_type
        raw_data["family_id"] = el.attrib.get('family-id', None)
        return DocDB(**raw_data)

    def epodoc_number(self, el, doc_type):
        raw_data = {
            "number": el.find("./epo:doc-number", NS),
            "kind": el.find("./epo:kind", NS),
            "date": el.find("./epo:date", NS),
        }
        for k, v in raw_data.items():
            if v is not None:
                raw_data[k] = v.text

        raw_data["doc_type"] = doc_type
        return EpoDoc(**raw_data)

    def cpc_class(self, el):
        keys = "section, class, subclass, main-group, subgroup".split(", ")
        data = {k: el.find("./epo:" + k, NS) for k in keys}
        data = {k: v.text for (k, v) in data.items() if v is not None}
        return f"{data.get('section', '')}{data.get('class', '')}{data.get('subclass', '')} {data.get('main-group', '')}/{data.get('subgroup', '')}"


class InpadocConnector(OpenPatentServicesConnector):
    page_size = 100
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

    def get_search_page(self, page_number, query):
        start = (page_number - 1) * self.page_size + 1
        end = start + self.page_size - 1
        params = {**query, **{"Range": f"{start}-{end}"}}
        text = self.xml_request(self.search_url, params)
        tree = ET.fromstring(text.encode("utf-8"))
        results = tree.findall(".//ops:publication-reference/epo:document-id", NS)
        return [
            self.docdb_number(el, "publication")
            for el in results
        ]

    def get_search_item(self, key, query_dict=None):
        query = self.create_query(query_dict)
        page_num = math.floor(key / self.page_size) + 1
        line_num = key % self.page_size
        page = self.get_search_page(page_num, query)
        return page[line_num]

    def get_search_length(self, query_dict=None):
        query = self.create_query(query_dict)
        params = {**query, **{"Range": f"1-{self.page_size}"}}
        text = self.xml_request(self.search_url, params)
        tree = ET.fromstring(text.encode("utf-8"))
        return int(tree.find(".//ops:biblio-search", NS).attrib["total-result-count"])

    def create_query(self, query_dict):
        if "cql_query" in query_dict:
            return dict(q=query_dict["cql_query"])
        query = ""
        for keyword, value in query_dict.items():
            if len(value.split()) > 1:
                value = f'"{value}"'
            query += SEARCH_FIELDS[keyword] + "=" + value + ' '
        return dict(q=query)

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
        tree = self.xml_data(doc_db, "biblio")
        documents = tree.findall("./epo:exchange-documents/epo:exchange-document", NS)

        data_items = list()
        for document in documents:
            data = dict()
            data["family_id"] = document.attrib["family-id"]

            bib_data = document.find("./epo:bibliographic-data", NS)

            title = bib_data.find("./epo:invention-title[@lang='en']", NS)
            if title is None:
                title = bib_data.find("./epo:invention-title", NS)
            if title is not None:
                data["title"] = title.text.strip()
            else:
                data["title"] = ""

            pub_data = bib_data.find(
                './epo:publication-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            pub_data = self.docdb_number(pub_data, "publication")
            data["doc_db"] = pub_data
            data["publication"] = pub_data.country + pub_data.number + pub_data.kind
            data["publication_date"] = pub_data.date
            data["country"] = pub_data.country

            app_data = bib_data.find(
                './epo:application-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            app_data = dict(self.docdb_number(app_data, "application")._asdict())
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

            data["intl_class"] = [
                whitespace_re.sub("", e.text)
                for e in bib_data.findall(
                    "./epo:classifications-ipcr/epo:classification-ipcr/epo:text", NS
                )
            ]

            data["cpc_class"] = [
                self.cpc_class(el)
                for el in bib_data.findall(
                    "./epo:patent-classifications/epo:patent-classification", NS
                )
            ]

            data["priority_claims"] = [
                e.text
                for e in bib_data.findall(
                    './epo:priority-claims/epo:priority-claim/epo:document-id[@document-id-type="original"]/epo:doc-number',
                    NS,
                )
            ]

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
        tree = self.xml_data(doc_db, "description")
        description = tree.find(
            "./ft:fulltext-documents/ft:fulltext-document/ft:description", NS
        )
        text = "\n".join(description.itertext()).strip()
        return text

    def claims(self, doc_db):
        tree = self.xml_data(doc_db, "claims")
        claim_text = [
            "".join(e.itertext()).strip()
            for e in tree.findall(
                './ft:fulltext-documents/ft:fulltext-document/ft:claims[@lang="EN"]/ft:claim/ft:claim-text',
                NS,
            )
        ]
        return clean_claims(claim_text)

    def images(self, doc_db):
        if doc_db.doc_type == "application":
            return dict()
        tree = self.xml_data(doc_db, "images")
        images = tree.find(
            './ops:document-inquiry/ops:inquiry-result/ops:document-instance[@desc="FullDocument"]',
            NS,
        )
        return {
            "url": "http://ops.epo.org/rest-services/" + images.attrib["link"] + ".pdf",
            "num_pages": int(images.attrib["number-of-pages"]),
            "sections": {
                e.attrib["name"]: int(e.attrib["start-page"])
                for e in images.findall("./ops:document-section", NS)
            },
        }

    def family(self, doc_db):
        tree = self.xml_data(doc_db, "family")
        doc_db_list = list()
        for el in tree.findall("./ops:patent-family/ops:family-member", NS):
            pub_ref = el.find(
                './epo:publication-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            if pub_ref is not None:
                doc_db_list.append(self.docdb_number(pub_ref, "publication"))
            else:
                app_ref = el.find(
                    './epo:application-reference/epo:document-id[@document-id-type="docdb"]',
                    NS,
                )
                doc_db_list.append(self.docdb_number(app_ref, "application"))
        return doc_db_list


class EpoConnector(OpenPatentServicesConnector):
    def xml_data(self, pub, data_kind):
        """
        Acceptable kinds are "biblio", "events", "procedural-steps"
        """
        case_number = f"EP.{pub.number[2:]}"
        if pub.kind:
            case_number += "." + pub.kind

        register_url = "http://ops.epo.org/3.2/rest-services/register/{doc_type}/epodoc/{case_number}/"
        if data_kind not in ("biblio", "events", "procedural-steps"):
            raise ValueError(data_kind + " is not a valid data kind")
        url = (
            register_url.format(case_number=case_number, doc_type=pub.doc_type)
            + data_kind
        )
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        return tree

    def status(self, el):
        return {
            "description": el.text,
            "code": el.attrib["status-code"],
            "date": el.attrib["change-date"],
        }

    def priority_claim(self, el):
        return {
            "kind": el.attrib["kind"],
            "number": el.find("./reg:doc-number", NS).text,
            "date": el.find("./reg:date", NS).text,
        }

    def docid(self, el):
        doc_id = el.find(".//reg:document-id", NS)
        raw = {
            "country": doc_id.find("./reg:country", NS),
            "number": doc_id.find("./reg:doc-number", NS),
            "kind": doc_id.find("./reg:kind", NS),
            "date": doc_id.find("./reg:date", NS),
        }
        return {k: v.text for (k, v) in raw.items() if v is not None}

    def party(self, el):
        addr_book = el.find("./reg:addressbook", NS)
        name = addr_book.find("./reg:name", NS)
        address = addr_book.find("./reg:address", NS)
        return {
            "name": name.text,
            "address": "\n".join(
                [t.strip() for t in address.itertext() if t.strip()]
            ).strip(),
        }

    def citation(self, el):
        phase = el.attrib["cited-phase"]
        office = el.attrib.get("office", "")
        pat_cite = el.find("./reg:patcit", NS)
        if pat_cite is not None:
            citation = self.docid(pat_cite)
        else:
            citation = el.find("./reg:nplcit/reg:text", NS).text
        category = (
            el.find("./reg:category", NS).text
            if el.find("./reg:category", NS) is not None
            else ""
        )
        relevant_passages = pat_cite.find("./reg:text", NS).text
        return {
            "phase": phase,
            "office": office,
            "citation": citation,
            "category": category,
            "relevant_passages": relevant_passages,
        }

    def step(self, el):
        date = el.find("./reg:procedural-step-date/reg:date", NS)
        return {
            "phase": el.attrib["procedure-step-phase"],
            "description": " - ".join(
                [e.text for e in el.findall("./reg:procedural-step-text", NS)]
            ),
            "date": date.text.strip() if date is not None else None,
            "code": el.find("./reg:procedural-step-code", NS).text.strip(),
        }

    def procedural_steps(self, epodoc):
        tree = self.xml_data(epodoc, "procedural-steps")
        doc = tree.find(".//reg:register-document", NS)
        return [self.step(el) for el in doc.find("./reg:procedural-data", NS)]

    def bib_data(self, epodoc):
        tree = self.xml_data(epodoc, "biblio")
        doc = tree.find(".//reg:register-document", NS)
        bib = doc.find("./reg:bibliographic-data", NS)
        parties = bib.find("./reg:parties", NS)
        output = dict()
        output["number"] = epodoc.number
        output["kind"] = epodoc.kind
        output["case_number"] = epodoc.number + epodoc.kind
        output["epodoc"] = epodoc
        output["doc_type"] = epodoc.doc_type
        output["status"] = [
            self.status(el) for el in doc.find("./reg:ep-patent-statuses", NS)
        ]
        output["publications"] = [
            self.docid(el) for el in bib.findall("./reg:publication-reference", NS)
        ]
        output["intl_class"] = [
            "".join(el.itertext()).strip()
            for el in bib.find("./reg:classifications-ipcr", NS)
        ]
        output["applications"] = [
            self.docid(el) for el in bib.findall("./reg:application-reference", NS)
        ]
        output["filing_language"] = bib.find("./reg:language-of-filing", NS).text
        output["priority_claims"] = [
            self.priority_claim(el) for el in bib.find("reg:priority-claims", NS)
        ]
        output["applicants"] = [
            self.party(el) for el in parties.find("./reg:applicants", NS)
        ]
        output["inventors"] = [
            self.party(el) for el in parties.find("./reg:inventors", NS)
        ]
        output["designated_states"] = [
            c.strip()
            for c in bib.find("./reg:designation-of-states", NS).itertext()
            if c.strip()
        ]
        output["title"] = bib.find('./reg:invention-title[@lang="en"]', NS).text
        output["citations"] = [
            self.citation(el) for el in bib.find("./reg:references-cited", NS)
        ]
        return output
