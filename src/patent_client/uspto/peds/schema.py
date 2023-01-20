from collections import defaultdict
from typing import *

from patent_client.util.format import clean_whitespace
from yankee.json.schema import fields as f
from yankee.json.schema import Schema


class InventorNameField(f.Combine):
    name_line_one = f.Str()
    name_line_two = f.Str()
    suffix = f.Str()

    def combine_func(self, obj):
        return clean_whitespace(
            f"{obj.get('name_line_one', '')}; {obj.get('name_line_two', '')} {obj.get('suffix', '')}"
        )


class InventorAddressField(f.Combine):
    street_one = f.Str()
    street_two = f.Str()
    city = f.Str()
    geo_code = f.Str()
    postal_code = f.Str()
    country = f.Str()

    def combine_func(self, obj):
        return clean_whitespace(
            f'{obj.street_one or ""}\n{obj.street_two or ""}\n{obj.city or ""}, {obj.geo_code or ""} {obj.postal_code or ""} {obj.country or ""}',
            preserve_newlines=True,
        )


class PersonSchema(Schema):
    name = InventorNameField(data_key=False)
    address = InventorAddressField(data_key=False)
    rank_no = f.Int()


class InventorSchema(PersonSchema):
    pass


class ApplicantSchema(PersonSchema):
    cust_no = f.Str()


class TransactionSchema(Schema):
    date = f.Date("recordDate")
    code = f.Str()
    description = f.Str()


class ChildSchema(Schema):
    __model_name__ = "Relationship"
    parent_appl_id = f.Str("applicationNumberText")
    child_app_filing_date = f.Date("filingDate")
    child_app_status = f.Str("applicationStatus")
    child_appl_id = f.Str("claimApplicationNumberText")
    relationship = f.Str(
        "applicationStatusDescription",
        formatter=lambda x: x.replace("This application ", ""),
    )


class ParentSchema(Schema):
    __model_name__ = "Relationship"
    parent_appl_id = f.Str("claimApplicationNumberText")
    child_appl_id = f.Str("applicationNumberText")
    parent_app_filing_date = f.Date("filingDate")
    parent_app_status = f.Str("applicationStatus")
    relationship = f.Str(
        "applicationStatusDescription",
        formatter=lambda x: x.replace("This application ", ""),
    )


class OptionalFloat(f.Int):
    def deserialize(self, elem) -> "Optional[int]":
        try:
            return super().deserialize(elem)
        except ValueError:
            return None


class PtaPteHistorySchema(Schema):
    date = f.Date("ptaOrPteDate")
    description = f.String("contentsDescription")
    number = f.Float()
    pto_days = OptionalFloat()
    applicant_days = OptionalFloat()
    start = f.Float()


class PtaPteSummarySchema(Schema):
    a_delay = f.Int()
    b_delay = f.Int()
    c_delay = f.Int()
    overlap_delay = f.Int()
    pto_delay = f.Int()
    applicant_delay = f.Int("applDelay")
    pto_adjustments = f.Int()
    total_days = f.Int("totalPtoDays")
    kind = f.Str("ptaPteInd")


class CorrespondentNameSchema(f.Combine):
    line_one = f.Str("corrAddrNameLineOne")
    line_two = f.Str("corrAddrNameLineTwo")

    def combine_func(self, obj):
        obj = defaultdict(lambda: "", obj.to_dict())
        return "{line_one}\n{line_two}".format_map(obj)


class CorrespondentAddressSchema(f.Combine):
    street_1 = f.Str("corrAddrStreetLineOne")
    street_2 = f.Str("corrAddrStreetLineTwo")
    city = f.Str("corrAddrCity")
    geo_code = f.Str("corrAddrGeoRegionCode")
    postal_code = f.Str("corrAddrPostalCode")
    country = f.Str(data_key="corrAddrCountryCd")

    def combine_func(self, obj):
        obj = defaultdict(lambda: "", obj.to_dict())
        return clean_whitespace(
            "{street_1}\n{street_2}\n{city}, {geo_code} {postal_code} {country}".format_map(obj),
            preserve_newlines=True,
        )


class CorrespondentSchema(Schema):
    name = CorrespondentNameSchema(data_key=False)
    address = CorrespondentAddressSchema(data_key=False)
    cust_no = f.Str("corrAddrCustNo")


class AttorneySchema(Schema):
    registration_no = f.Str()
    name = f.Str("fullName")
    phone_num = f.Str()
    reg_status = f.Str()


class ForeignPrioritySchema(Schema):
    priority_claim = f.Str()
    country_name = f.Str()
    filing_date = f.Date(dt_format="%m-%d-%Y")


class DocumentSchema(Schema):
    access_level_category = f.Str()
    appl_id = f.Str("applicationNumberText")
    category = f.Str("documentCategory")
    code = f.Str(data_key="documentCode")
    description = f.Str("documentDescription")
    identifier = f.Str("documentIdentifier")
    mail_room_date = f.Date()
    page_count = f.Int()
    url = f.Str(data_key="pdf_url")


class ReelFrameField(f.Combine):
    reel_number = f.Str()
    frame_number = f.Str()

    def combine_func(self, obj):
        return f"{obj.reel_number}/{obj.frame_number}"


class AddressField(f.Combine):
    line_1 = f.Str("addressLineOneText", null_value="null")
    line_2 = f.Str("addressLineTwoText", null_value="null")
    line_3 = f.Str("addressLineThreeText", null_value="null")
    line_4 = f.Str("addressLineFourText", null_value="null")

    def combine_func(self, obj):
        return clean_whitespace(
            f"{obj.get('line_1', '')}\n{obj.get('line_2', '')}\n{obj.get('line_3', '')}\n{obj.get('line_4', '')}".strip(),
            preserve_newlines=True,
        )


class AssignorSchema(Schema):
    name = f.Str("assignorName")
    exec_date = f.Date()


class AssigneeAddressField(f.Combine):
    line_1 = f.Str("streetLineOneText", null_value="null")
    line_2 = f.Str("streetLineTwoText", null_value="null")
    city = f.Str("cityName")
    country = f.Str("countryCode")
    postal_code = f.Str("postalCode")

    def combine_func(self, obj):
        return clean_whitespace(
            f"{obj.get('line_1', '')}\n{obj.get('line_2', '')}\n{obj.get('city', '')}, {obj.get('country', '')} {obj.get('postal_code', '')}",
            preserve_newlines=True,
        )


class AssigneeSchema(Schema):
    name = f.Str("assigneeName")
    address = AssigneeAddressField(data_key=False)


class AssignmentSchema(Schema):
    id = ReelFrameField(data_key=False)
    correspondent = f.Str("addressNameText")
    correspondent_address = AddressField(data_key=False)
    mail_date = f.Date(null_value="NONE")
    received_date = f.Date(null_value="NONE")
    recorded_date = f.Date(null_value="NONE")
    pages = f.Int("pagesCount")
    conveyance_text = f.Str(
        "converyanceName",
        formatter=lambda x: x.replace(" (SEE DOCUMENT FOR DETAILS).", ""),
    )
    sequence_number = f.Int()
    assignors = f.List(AssignorSchema, "assignors")
    assignees = f.List(AssigneeSchema, "assignee")


class USApplicationSchema(Schema):
    # Basic Bibliographic Data
    appl_id = f.Str()
    app_confr_number = f.Str()
    app_filing_date = f.Date()
    app_location = f.Str()
    app_type = f.Str()
    app_entity_status = f.Str()
    app_cls_sub_cls = f.Str()
    app_grp_art_number = f.Str()
    app_exam_name = f.Str()
    first_inventor_file = f.Bool(true_value="Yes")
    patent_title = f.Str()
    # Status Information
    app_status = f.Str()
    app_status_date = f.Date()
    # Publication Information
    app_early_pub_number = f.Str()
    app_early_pub_date = f.Date()
    patent_number = f.Str()
    patent_issue_date = f.Date()
    wipo_early_pub_number = f.Str()
    wipo_early_pub_date = f.Date()
    # Correspondent / Attorney Information
    corr_addr_cust_no = f.Str()
    app_cust_number = f.Str()
    app_attr_dock_number = f.Str()

    # Assignments
    assignments = f.List(AssignmentSchema)

    # Parties
    inventors = f.List(InventorSchema)
    applicants = f.List(ApplicantSchema)
    transactions = f.List(TransactionSchema)
    child_continuity = f.List(ChildSchema)
    parent_continuity = f.List(ParentSchema)
    pta_pte_tran_history = f.List(PtaPteHistorySchema)
    pta_pte_summary = PtaPteSummarySchema(data_key=False)
    correspondent = CorrespondentSchema(data_key=False)
    attorneys = f.List(AttorneySchema, data_key="attrnyAddr")
    foreign_priority = f.List(ForeignPrioritySchema)


class PedsPageSchema(Schema):
    index_last_updated = f.Date("queryResults.indexLastUpdatedDate")
    num_found = f.Int("queryResults.searchResponse.response.numFound")
    applications = f.List(USApplicationSchema, "queryResults.searchResponse.response.docs")
