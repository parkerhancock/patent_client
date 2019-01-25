
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ns = dict(
    uspat="urn:us:gov:doc:uspto:patent",
    pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent",
    uscom="urn:us:gov:doc:uspto:common",
    com="http://www.wipo.int/standards/XMLSchema/ST96/Common",
    xsi="http://www.w3.org/2001/XMLSchema-instance",
)


bib_data = dict(
    appl_id=".//uscom:ApplicationNumberText",
    app_filing_date=".//pat:FilingDate",
    app_type=".//uscom:ApplicationTypeCategory",
    app_cust_number=".//com:ContactText",
    app_group_art_unit=".//uscom:GroupArtUnitNumber",
    app_atty_dock_number=".//com:ApplicantFileReference",
    patent_title=".//pat:InventionTitle",
    app_status=".//uscom:ApplicationStatusCategory",
    app_status_date=".//uscom:ApplicationStatusDate",
    app_cls_subcls=".//pat:NationalSubclass",
    app_early_pub_date=".//uspat:PatentPublicationIdentification/com:PublicationDate",
    patent_number=".//uspat:PatentGrantIdentification/pat:PatentNumber",
    patent_issue_date=".//uspat:PatentGrantIdentification/pat:GrantDate",
    aia_status=".//uspat:FirstInventorToFileIndicator",
    app_entity_status=".//uscom:BusinessEntityStatusCategory",
    file_location=".//uscom:OfficialFileLocationCategory",
    file_location_date=".//uscom:OfficialFileLocationDate",
    app_examiner=".//pat:PrimaryExaminer//com:PersonFullName",
)


inv_data = dict(
    name="./com:PublicationContact/com:Name/com:PersonName",
    city="./com:PublicationContact/com:CityName",
    country="./com:PublicationContact/com:CountryCode",
    region="./com:PublicationContact/com:GeographicRegionName",
)

ph_data = dict(date="./uspat:RecordedDate", action="./uspat:CaseActionDescriptionText")

WHITESPACE_RE = re.compile(r"\s+")

class USApplicationXmlParser:
    def element_to_text(self, element):
        return WHITESPACE_RE.sub(" ", " ".join(element.itertext())).strip()

    def parse_element(self, element, data_dict):
        data = {
            key: self.element_to_text(element.find(value, ns))
            for (key, value) in data_dict.items()
            if element.find(value, ns) is not None
        }
        for key in data.keys():
            if "date" in key and data.get(key, False) != "-":
                data[key] = parse_dt(data[key]).date()
            elif data.get(key, False) == "-":
                data[key] = None
        return data

    def parse_bib_data(self, element):
        data = self.parse_element(element, bib_data)
        pub_no = element.find(
            ".//uspat:PatentPublicationIdentification/pat:PublicationNumber", ns
        )
        if pub_no is not None:
            if len(pub_no.text) > 7:
                pub_no = pub_no.text
            else:
                pub_no = str(data["app_early_pub_date"].year) + pub_no.text

            if len(pub_no) < 11:
                pub_no = pub_no[:4] + pub_no[4:].rjust(7, "0")

            kind_code = element.find(
                ".//uspat:PatentPublicationIdentification/com:PatentDocumentKindCode",
                ns,
            )
            if kind_code is None:
                kind_code = ""
            else:
                kind_code = kind_code.text
            data["app_early_pub_number"] = pub_no + kind_code
        return data

    def parse_transaction_history(self, element):
        output = list()
        for event_el in element.findall(
            "./uspat:PatentRecord/uspat:ProsecutionHistoryData", ns
        ):
            event = self.parse_element(event_el, ph_data)
            event["action"], event["code"] = event["action"].rsplit(" , ", 1)
            output.append(event)
        return output

    def parse_inventors(self, element):
        output = list()
        for inv_el in element.findall(
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/pat:PartyBag/pat:InventorBag/pat:Inventor",
            ns,
        ):
            data = self.parse_element(inv_el, inv_data)
            data["region_type"] = inv_el.find(
                "./com:PublicationContact/com:GeographicRegionName", ns
            ).attrib.get(
                "{http://www.wipo.int/standards/XMLSchema/ST96/Common}geographicRegionCategory",
                "",
            )
            output.append(data)
        return output

    def parse_applicants(self, element):
        output = list()
        for app_el in element.findall(
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/pat:PartyBag/pat:ApplicantBag/pat:Applicant",
            ns,
        ):
            data = self.parse_element(app_el, inv_data)
            data["region_type"] = app_el.find(
                "./com:PublicationContact/com:GeographicRegionName", ns
            ).attrib.get(
                "{http://www.wipo.int/standards/XMLSchema/ST96/Common}geographicRegionCategory",
                "",
            )
            output.append(data)
        return output

    def case(self, element):
        return {
            **self.parse_bib_data(element),
            **dict(
                inventors=self.parse_inventors(element),
                transactions=self.parse_transaction_history(element),
                applicants=self.parse_applicants(element),
            ),
        }

    def xml_file(self, file_obj):
        try:
            for _, element in ET.iterparse(file_obj):
                if "PatentRecordBag" in element.tag:
                    yield element
        except ET.ParseError as e:
            print(e)

    def save_state(state):
        with open("pdb_state.json", "w") as f:
            json.dump(state, f, indent=2)

