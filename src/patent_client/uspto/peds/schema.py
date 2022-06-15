import re
from importlib import import_module
from yankee.json.schema import Schema, fields as f

whitespace_except_newlines_re = re.compile(r"[ \t\r\f\v]+")
newlines_re = re.compile(r"\n+")

def clean_whitespace(string, preserve_newlines=False):
    string = string.strip()
    string = whitespace_except_newlines_re.sub(" ", string)
    if preserve_newlines:
        string = newlines_re.sub("\n", string)
    else:
        string = newlines_re.sub(" ", string)
    return string

class Default(dict):
    def __init__(self, *args, default=None, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        return self.default

class PedsSchema(Schema):
    __model_name__ = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_name = self.__model_name__ or self.__class__.__name__.replace("Schema", "")
        model_module = import_module("..model", __name__)
        self.__model__ = getattr(model_module, model_name)

    def post_load(self, obj):
        if obj:
            return self.__model__(**obj)
        else:
            return None

class InventorNameField(f.Combine):
    name_line_one = f.Str()
    name_line_two = f.Str()
    suffix = f.Str()

    def combine_func(self, obj):
        return clean_whitespace(f"{obj.get('name_line_one', '')}; {obj.get('name_line_two', '')} {obj.get('suffix', '')}")

class InventorAddressField(f.Combine):
    street_one = f.Str()
    street_two = f.Str()
    city = f.Str()
    geo_code = f.Str()
    postal_code = f.Str()
    country = f.Str()

    def combine_func(self, obj):
        obj = Default(**obj, default='')
        return clean_whitespace(
            "{street_1}\n{street_2}\n{city}, {geo_code} {postal_code} {country}".format_map(obj),
            preserve_newlines=True
        )


class InventorSchema(PedsSchema):
    name = InventorNameField(data_key=False)
    address = InventorAddressField(data_key=False)
    rank_no = f.Int()

class ApplicantSchema(InventorSchema):
    cust_no = f.Str()

class TransactionSchema(PedsSchema):
    date = f.Date("recordDate")
    code = f.Str()
    description = f.Str()

class ChildSchema(PedsSchema):
    __model_name__ = "Relationship"
    parent_appl_id = f.Str('applicationNumberText')
    child_app_filing_date = f.Date('filingDate')
    child_app_status = f.Str('applicationStatus')
    child_appl_id = f.Str('claimApplicationNumberText')
    relationship = f.Str('applicationStatusDescription',
        formatter=lambda x: x.replace('This application ', ''))

class ParentSchema(PedsSchema):
    __model_name__ = "Relationship"
    parent_appl_id = f.Str('claimApplicationNumberText')
    child_appl_id = f.Str('applicationNumberText')
    parent_app_filing_date = f.Date('filingDate')
    parent_app_status = f.Str('applicationStatus')
    relationship = f.Str('applicationStatusDescription',
        formatter=lambda x: x.replace('This application ', ''))

class OptionalFloat(f.Int):
    def deserialize(self, elem) -> "Optional[int]":
        try:
            return super().deserialize(elem)
        except ValueError:
            return None

class PtaPteHistorySchema(PedsSchema):
    date = f.Date("ptaOrPteDate")
    description = f.String("contentsDescription")
    number = f.Float()
    pto_days = OptionalFloat()
    applicant_days = OptionalFloat()
    start = f.Float()
    
class PtaPteSummarySchema(PedsSchema):
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
        obj = Default(**obj, default='')
        return "{line_one}\n{line_two}".format_map(obj)

class CorrespondentAddressSchema(f.Combine):
    street_1 = f.Str("corrAddrStreetLineOne")
    street_2 = f.Str("corrAddrStreetLineTwo")
    city = f.Str("corrAddrCity")
    geo_code = f.Str("corrAddrGeoRegionCode")
    postal_code = f.Str("corrAddrPostalCode")
    country = f.Str(data_key="corrAddrCountryCd")

    def combine_func(self, obj):
        obj = Default(**obj, default='')
        return clean_whitespace(
            "{street_1}\n{street_2}\n{city}, {geo_code} {postal_code} {country}".format_map(obj),
            preserve_newlines=True
            )

class CorrespondentSchema(PedsSchema):
    name = CorrespondentNameSchema(data_key=False)
    address = CorrespondentAddressSchema(data_key=False)
    cust_no = f.Str("corrAddrCustNo")

class AttorneySchema(PedsSchema):
    registration_no = f.Str()
    name = f.Str("fullName")
    phone_num = f.Str()
    reg_status = f.Str()

class ForeignPrioritySchema(PedsSchema):
    priority_claim = f.Str()
    country_name = f.Str()
    filing_date = f.Date(dt_format="%m-%d-%Y")

class USApplicationSchema(PedsSchema):
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
    app_early_pub_date = f.Str()
    patent_number = f.Str()
    patent_issue_date = f.Str()
    wipo_early_pub_number = f.Str()
    wipo_early_pub_date = f.Date()
    # Correspondent / Attorney Information
    corr_addr_cust_no = f.Str()
    app_cust_number = f.Str()
    app_attr_dock_number= f.Str()

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

class DocumentSchema(PedsSchema):
    access_level_category = f.Str()
    appl_id = f.Str("applicationNumberText")
    category = f.Str("documentCategory")
    code = f.Str(data_key="documentCode")
    description = f.Str("documentDescription")
    identifier = f.Str("documentIdentifier")
    mail_room_date = f.Date()
    page_count = f.Int()
    url = f.Str(data_key="pdf_url")