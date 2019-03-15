
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from dateutil.parser import parse as parse_dt
from copy import deepcopy

ns = dict(
    uspat="urn:us:gov:doc:uspto:patent",
    pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent",
    uscom="urn:us:gov:doc:uspto:common",
    com="http://www.wipo.int/standards/XMLSchema/ST96/Common",
    xsi="http://www.w3.org/2001/XMLSchema-instance",
)


bib_data = dict(
    appl_id=".//uscom:ApplicationNumberText",
    app_confr_number = ".//uspat:ApplicationConfirmationNumber",
    app_filing_date=".//pat:FilingDate",
    app_type=".//uscom:ApplicationTypeCategory",
    app_cust_number="./uspat:PatentRecord/uspat:PatentCaseMetadata/uspat:PartyBag/com:CorrespondenceAddress/com:PartyIdentifier",
    corr_addr_cust_no="./uspat:PatentRecord/uspat:PatentCaseMetadata/uspat:PartyBag/com:CorrespondenceAddress/com:PartyIdentifier",
    app_grp_art_number=".//uscom:GroupArtUnitNumber",
    app_attr_dock_number=".//com:ApplicantFileReference",
    patent_title=".//pat:InventionTitle",
    app_status=".//uscom:ApplicationStatusCategory",
    app_status_date=".//uscom:ApplicationStatusDate",
    #app_cls_subcls=".//pat:PatentClassificationBag/pat:NationalClassification/pat:MainNationalClassification",
    app_early_pub_date=".//uspat:PatentPublicationIdentification/com:PublicationDate",
    patent_number=".//uspat:PatentGrantIdentification/pat:PatentNumber",
    patent_issue_date=".//uspat:PatentGrantIdentification/pat:GrantDate",
    first_inventor_file=".//uspat:FirstInventorToFileIndicator",
    app_entity_status=".//uscom:BusinessEntityStatusCategory",
    app_location=".//uscom:OfficialFileLocationCategory",
    file_location_date=".//uscom:OfficialFileLocationDate",
    app_exam_name=".//pat:PrimaryExaminer//com:PersonFullName",
)

correspondent_data = dict(
    corr_addr_name_line_one='./com:Contact/com:Name/com:PersonName/com:PersonStructuredName/com:LastName',
    corr_addr_city='./com:Contact/com:PostalAddressBag/com:PostalAddress/com:PostalStructuredAddress/com:CityName',
    corr_addr_geo_region_code='./com:Contact/com:PostalAddressBag/com:PostalAddress/com:PostalStructuredAddress/com:GeographicRegionName',
    corr_addr_postal_code='./com:Contact/com:PostalAddressBag/com:PostalAddress/com:PostalStructuredAddress/com:PostalCode',
)

inv_data = dict(
    name="./com:PublicationContact/com:Name/com:PersonName",
    city="./com:PublicationContact/com:CityName",
    country="./com:PublicationContact/com:CountryCode",
    region="./com:PublicationContact/com:GeographicRegionName",
)

applicant_data = dict(
    nameLineOne="./com:Name/com:PersonName/com:PersonStructuredName/com:LastName",
    city = "./com:CityName",
    geoCode = "./com:GeographicRegionName",
    country = "./com:CountryCode"
)

ph_data = dict(recordDate="./uspat:EventDate", action="./uspat:EventDescriptionText")

child_data = dict(
    claim_application_number_text="./com:ApplicationNumberText",
    filing_date="./pat:FilingDate",
    patent_number_text="./pat:PatentNumber",
    application_status="./uspat:ChildDocumentStatusCode",
    application_status_description="./uscom:DescriptionText",
)


parent_data = deepcopy(child_data)
parent_data['application_status'] = "./uspat:ParentDocumentStatusCode"

foreign_priority_data = dict(
    countryName='./uscom:IPOfficeName',
    applicationNumberText='./com:ApplicationNumber/com:ApplicationNumberText',
    filingDate='./pat:FilingDate',
)

pta_history_data = dict(
    number='./uspat:EventSequenceNumber',
    pta_or_pte_date='./uspat:EventDate',
    contents_description='./uspat:EventDescriptionText',
    pto_days='uspat:IPOfficeDayDelayQuantity',
    appl_days='uspat:ApplicantDayDelayQuantity',
    start='uspat:OriginatingEventSequenceNumber',
)

pta_summary_data = dict(
    pto_adjustments="./uspat:IPOfficeDayDelayQuantity",
    overlap_delay="./uspat:OverlappingDayQuantity",
    a_delay="./uspat:ADelayQuantity",
    b_delay="./uspat:BDelayQuantity",
    c_delay="./uspat:CDelayQuantity",
    pto_delay="./uspat:NonOverlappingDayQuantity",
    appl_delay="./uspat:ApplicantDayDelayQuantity",
    total_pto_days="./uspat:AdjustmentTotalQuantity",
)

attorney_data = dict(
    registration_no='./pat:RegisteredPractitionerRegistrationNumber',
    category='./pat:RegisteredPractitionerCategory',
    first_name='./com:Contact/com:Name/com:PersonName/com:PersonStructuredName/com:FirstName',
    middle_name='./com:Contact/com:Name/com:PersonName/com:PersonStructuredName/com:MiddleName',
    last_name='./com:Contact/com:Name/com:PersonName/com:PersonStructuredName/com:LastName',
    phone_num='./com:Contact/com:PhoneNumberBag/com:PhoneNumber',
)

WHITESPACE_RE = re.compile(r"\s+")
child_status_re = re.compile(r'^which is ([^\s]+) ')
reference_re = re.compile(r' \d+$')

class XMLParsingException(Exception):
    pass

class USApplicationXmlParser:
    def element_to_text(self, element):
        return WHITESPACE_RE.sub(" ", " ".join(element.itertext())).strip()

    def parse_element(self, element, data_dict):
        data = {
            key: self.element_to_text(element.find(value, ns))
            for (key, value) in data_dict.items()
            if element and element.find(value, ns) is not None
        }
        for key in data.keys():
            if "date" in key and data.get(key, False) != "-":
                data[key] = parse_dt(data[key]).date()
            elif data.get(key, False) == "-":
                data[key] = None
        return data

    def parse_pta_history(self, element):
        output = list()
        for row in element.findall('.//uspat:PatentTermAdjustmentHistoryData', ns):
            output.append(self.parse_element(row, pta_history_data))
        return output

    def parse_correspondent(self, element):
        el = element.find('.//com:CorrespondenceAddress', ns)
        if not el:
            return dict()
        cor_data = self.parse_element(el, correspondent_data)
        address_lines = el.findall('./com:Contact/com:PostalAddressBag/com:PostalAddress/com:PostalStructuredAddress/com:AddressLineText', ns)
        line_nos = 'one, two, three'.split(', ')
        for i, a in enumerate(address_lines):
            cor_data['corr_addr_street_line_' + line_nos[i]] = a.text
        return cor_data

    def parse_pta_summary(self, element):
        summary = element.find('.//uspat:PatentTermAdjustmentData', ns)
        if not summary:
            return dict()
        data = self.parse_element(summary, pta_summary_data)
        data['pta_pte_ind'] = 'PTA'
        return data

    def parse_attorneys(self, element):
        attorneys = element.findall('.//uspat:RegisteredPractitioner', ns)
        output = list()
        for a in attorneys:
            a_data = self.parse_element(a, attorney_data)
            full_name = [a_data[k] for k in 'first_name, middle_name, last_name'.split(', ') if a_data[k]]
            status_indicator = a.get('{urn:us:gov:doc:uspto:common}activeIndicator')
            if status_indicator == 'true':
                status = 'ACTIVE'
            else:
                status = 'INACTIVE'
            output.append({
                'registration_no': a_data.get('registration_no', None),
                'full_name': ' '.join(full_name),
                'phone_num': a_data.get('phone_num', None),
                'reg_status': status,
            })
        return output


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
            if 'PCT' in data['appl_id']:
                data["app_early_pub_number"] = f"WO/{pub_no[:4]}/{pub_no[4:]}"
            else:
                data["app_early_pub_number"] = pub_no + kind_code

        classification_data = element.find('./uspat:PatentRecord/uspat:PatentCaseMetadata/pat:PatentClassificationBag/pat:NationalClassification/pat:MainNationalClassification', ns)
        if classification_data:
            us_class = classification_data.find('./pat:NationalClass', ns)
            us_sub_class = classification_data.find('./pat:NationalSubclass', ns)
            if us_class and us_sub_class:
                data['app_cls_sub_cls'] = f'{us_class.text}/{us_sub_class.text}'
        else:
            data['app_cls_sub_cls'] = None
        return data

    def parse_transaction_history(self, element):
        output = list()
        for event_el in element.findall(
            "./uspat:PatentRecord/uspat:ProsecutionHistoryDataBag/uspat:ProsecutionHistoryData", ns
        ):
            event = self.parse_element(event_el, ph_data)
            event["description"], event["code"] = event["action"].rsplit(" , ", 1)
            del event['action']
            output.append(event)
        return output

    def parse_inventors(self, element):
        output = list()
        for inv_el in element.findall(
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/uspat:PartyBag/pat:InventorBag/pat:Inventor",
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
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/uspat:PartyBag/pat:ApplicantBag/pat:Applicant/com:PublicationContact",
            ns,
        ):
            expected_els = 'city, country, geoCode, nameLineOne, nameLineTwo, rankNo, streetOne, streetTwo, suffix'.split(', ')
            expected_data = {k: '' for k in expected_els}
            data = {**expected_data, **self.parse_element(app_el, applicant_data)}
            
            output.append(data)
        return output

    
    def parse_children(self, element):
        output=list()
        for child in element.findall("./uspat:PatentRecord/uspat:PatentCaseMetadata/uspat:RelatedDocumentData/uspat:ChildDocumentData",
            ns,
            ):
            child_record = self.parse_element(child, child_data)
            description = child_record.get('application_status_description', '')
            if description:
                child_status_match = child_status_re.search(description)
                if child_status_match:
                    child_record['application_status'] = child_status_match.group(1)
                new_description = child_status_re.sub('', description)
                new_description = reference_re.sub('', new_description)
                child_record['application_status_description'] = new_description 
            output.append(child_record)

        return output

    def parse_parents(self, element):
        output=list()
        for child in element.findall("./uspat:PatentRecord/uspat:PatentCaseMetadata/uspat:RelatedDocumentData/uspat:ParentDocumentData",
            ns,
            ):
            output.append(self.parse_element(child, child_data))
        return output

    def parse_foreign_priority(self, element):
        output = list()
        for case in element.findall("./uspat:PatentRecord/uspat:PatentCaseMetadata/uspat:PriorityClaimBag/uspat:PriorityClaim", ns):
            output.append(self.parse_element(case, foreign_priority_data))
        return output

    def case(self, element):
        try:
            return {
                **self.parse_bib_data(element),
                **dict(
                    inventors=self.parse_inventors(element),
                    transactions=self.parse_transaction_history(element),
                    applicants=self.parse_applicants(element),
                    parent_continuity=self.parse_parents(element),
                    child_continuity=self.parse_children(element),
                    foreign_priority=self.parse_foreign_priority(element),
                    pta_pte_tran_history=self.parse_pta_history(element),
                    attrny_addr=self.parse_attorneys(element),
                ),
                **self.parse_pta_summary(element),
                **self.parse_correspondent(element),
            }
        except Exception as e:
            raise XMLParsingException('XML Parsing Error!')

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

