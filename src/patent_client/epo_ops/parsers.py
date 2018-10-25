import re
from collections import namedtuple

from lxml import etree as ET

# XML Namespaces for ElementTree
NS = {
    "ops": "http://ops.epo.org",
    "epo": "http://www.epo.org/exchange",
    "ft": "http://www.epo.org/fulltext",
    "reg": "http://www.epo.org/register",
}
DocDB = namedtuple("DocDB", ["country", "number", "kind", "date", "doc_type"])
EpoDoc = namedtuple("EpoDoc", ["number", "kind", "date"])
whitespace_re = re.compile(" +")
country_re = re.compile(r"^[A-Z]{2}")
ep_case_re = re.compile(r"EP(?P<number>[\d]+)(?P<kind>[A-Z]\d)?")


class OPSParser:
    """Internal xml parsing class for common tasks"""

    def docdb_number(self, el, doc_type):
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

    def epodoc_number(self, el):
        raw_data = {
            "number": el.find("./epo:doc-number", NS),
            "kind": el.find("./epo:kind", NS),
            "date": el.find("./epo:date", NS),
        }
        for k, v in raw_data.items():
            if v is not None:
                raw_data[k] = v.text

        return EpoDoc(**raw_data)

    def cpc_class(self, el):
        keys = "section, class, subclass, main-group, subgroup".split(", ")
        data = {k: el.find("./epo:" + k, NS) for k in keys}
        data = {k: v.text for (k, v) in data.items() if v is not None}
        return f"{data.get('section', '')}{data.get('class', '')}{data.get('subclass', '')} {data.get('main-group', '')}/{data.get('subgroup', '')}"

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

    def citation(self, el):
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


class InpadocParser(OPSParser):
    """
    INPADOC Publication

    This is a lazy-loading object that accesses INPADOC data for the associated class.
    
    The first time any data is accessed, the result is fetched and then cached on the object.

    Data includes:
        bib_data => Basic bibliogrpahic information + Abstract
        description => Full Text Specification
        claims => Claims text
        images => Images listing
        download_images() => download a PDF of the published document
        legal => Status Information

    """

    def __init__(self, manager):
        self.manager = manager

    def legal(self, doc_db):
        tree = self.manager.xml_data(doc_db, "legal")
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
            pub_data = self.manager.parser.docdb_number(pub_data, "publication")
            data["doc_db"] = pub_data
            data["publication"] = pub_data.country + pub_data.number + pub_data.kind
            data["publication_date"] = pub_data.date
            data["country"] = pub_data.country

            app_data = bib_data.find(
                './epo:application-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            app_data = dict(
                self.manager.parser.docdb_number(app_data, "application")._asdict()
            )
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
            data["references_cited"] = [
                self.manager.parser.citation(c) for c in refs_cited
            ]
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
