from pprint import pprint
from collections import OrderedDict
from marshmallow import Schema, fields, EXCLUDE, pre_load, post_load, ValidationError
from .model import USApplication, Relationship, PtaPteHistory, PtaPteSummary, Transaction, Correspondent, Attorney, Applicant, Inventor 
import inflection
from dateutil.parser import parse as parse_date

from patent_client.util import QuerySet, ListField

def create_subset(data, name, keys):
    subset = {k: data.pop(k) for k in keys if k in data}
    if subset:
        data[name] = subset
    return data

def create_subset_from_prefix(data, prefix):
    keys = [k for k in data.keys() if k.startswith(prefix)]
    return create_subset(data, prefix, keys)

def group_lines(data, prefix, delimiter='\n'):
    words = ('one', 'two', 'three', 'four')
    subset = list(k for k in tuple(data.keys()) if k.startswith(prefix) and '_line_' in k)
    ordered_keys = tuple(sorted(subset, key=lambda x: words.index(x.split('_')[-1])))
    data[prefix] = delimiter.join(data[k] for k in ordered_keys).strip()
    for k in subset:
        del data[k]
    return data


pta_pte_summary_keys = ("a_delay", "b_delay", "c_delay", "overlap_delay", "pto_delay", "appl_delay", "pto_adjustments", "total_pto_days", "pta_pte_ind",)

class ParsedDate(fields.Field):
    def _deserialize(self, value, attr, obj, **kwargs):
        try:
            return parse_date(value).date()
        except Exception as e:
            return None

class BaseSchema(Schema):
    pr = False
    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data = {inflection.underscore(k): v for k, v in input_data.items()}
        input_data = create_subset(input_data, 'pta_pte_summary', pta_pte_summary_keys)
        input_data = create_subset_from_prefix(input_data, 'corr_addr')
        
        if self.pr: pprint(input_data)
        return input_data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)
    
    class Meta:
        unknown = EXCLUDE
        dateformat = "%m-%d-%Y"

class ChildSchema(BaseSchema):
    __model__ = Relationship
    parent_appl_id = fields.Str(data_key='application_number_text')
    child_appl_id = fields.Str(data_key='claim_application_number_text')
    parent_app_filing_date = fields.Date(allow_none=True)
    relationship = fields.Function(
        deserialize=lambda x: x.replace('This application ', ''), 
        data_key='application_status_description')

class ParentSchema(BaseSchema):
    __model__ = Relationship
    parent_appl_id = fields.Str(data_key='claim_application_number_text')
    child_appl_id = fields.Str(data_key='application_number_text')
    parent_app_filing_date = fields.Date(data_key='filing_date')
    relationship = fields.Function(
        deserialize=lambda x: x.replace('This application ', ''), 
        data_key='application_status_description')

class PtaPteHistorySchema(BaseSchema):
    __model__ = PtaPteHistory
    number = fields.Float()
    date = fields.Date(data_key='pta_or_pte_date')
    description = fields.Str(data_key='contents_description')
    pto_days = fields.Int(allow_none=True)
    applicant_days = fields.Int(allow_none=True, data_key='appl_days')
    start = fields.Float()

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data = super(PtaPteHistorySchema, self).pre_load(input_data, **kwargs)
        input_data = {k:v if v else None for k, v in input_data.items()}
        return input_data

class PtaPteSummarySchema(BaseSchema):
    __model__ = PtaPteSummary
    a_delay = fields.Int()
    b_delay = fields.Int()
    c_delay = fields.Int()
    overlap_delay = fields.Int()
    pto_delay = fields.Int()
    applicant_delay = fields.Int(data_key='appl_delay')
    pto_adjustments = fields.Int()
    total_days = fields.Int(data_key='total_pto_days')
    kind = fields.Str(data_key='pta_pte_ind')

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data = super(PtaPteSummarySchema, self).pre_load(input_data, **kwargs)
        input_data = input_data['pta_pte_summary']
        from pprint import pprint
        return input_data

class TransactionSchema(BaseSchema):
    __model__ = Transaction
    date = ParsedDate(data_key='record_date')
    code = fields.Str()
    description = fields.Str()

    class Meta:
        unknown = EXCLUDE
        dateformat = "%m-%d-%Y"

class AttorneySchema(BaseSchema):
    __model__ = Attorney
    registration_no = fields.Str(allow_none=True)
    full_name = fields.Str()
    phone_num = fields.Str()
    reg_status = fields.Str(allow_none=True)

class CorrespondentSchema(BaseSchema):
    __model__ = Correspondent
    name = fields.Str()
    cust_no = fields.Str()
    street = fields.Str()
    city = fields.Str()
    geo_region_code = fields.Str()
    postal_code = fields.Str()
    country = fields.Str(data_key='country_cd')

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data = super(CorrespondentSchema, self).pre_load(input_data, **kwargs)
        input_data = input_data['corr_addr']
        input_data = {k[len('corr_addr_'):]:v for k,v in input_data.items()}
        input_data = group_lines(input_data, 'name')
        input_data = group_lines(input_data, 'street')
        return input_data

class ApplicantSchema(BaseSchema):
    __model__ = Applicant
    name = fields.Str()
    cust_no = fields.Str()
    street = fields.Str()
    city = fields.Str()
    geo_region_code = fields.Str()
    postal_code = fields.Str()
    country = fields.Str(data_key='country_cd')
    rank_no = fields.Int()

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data = super(ApplicantSchema, self).pre_load(input_data, **kwargs)
        input_data = group_lines(input_data, 'name')
        input_data = group_lines(input_data, 'street')
        return input_data

class InventorSchema(BaseSchema):
    __model__ = Inventor
    name = fields.Str()
    street = fields.Str()
    rank_no = fields.Int()
    city = fields.Str()
    geo_code = fields.Str()
    postal_code = fields.Str()
    country = fields.Str(data_key='country_cd')

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data = super(InventorSchema, self).pre_load(input_data, **kwargs)
        input_data = group_lines(input_data, 'name', delimiter='; ')
        input_data = group_lines(input_data, 'street')
        return input_data


class USApplicationSchema(BaseSchema):
    __model__ = USApplication
    appl_id = fields.Str()
    app_filing_date = ParsedDate()
    app_exam_name = fields.Str()
    app_early_pub_number = fields.Str(allow_none=True)
    app_early_pub_date = ParsedDate(allow_none=True)
    app_location = fields.Str()
    app_grp_art_number = fields.Str()
    patent_number = fields.Str(allow_none=True)
    patent_issue_date = ParsedDate(allow_none=True)
    app_status = fields.Str()
    app_status_date = ParsedDate()
    patent_title = fields.Str()
    app_attr_dock_number = fields.Str(allow_none=True)
    first_inventor_file = fields.Str()
    app_type = fields.Str()
    app_cust_number = fields.Str(allow_none=True)
    app_cls_sub_cls = fields.Str()
    corr_addr_cust_no = fields.Str(allow_none=True)
    app_entity_status = fields.Str()
    app_confr_number = fields.Str()
    wipo_early_pub_number = fields.Str()
    wipo_early_pub_date = ParsedDate()
    child_continuity = ListField(fields.Nested(ChildSchema()))
    parent_continuity = ListField(fields.Nested(ParentSchema()))
    pta_pte_tran_history = ListField(fields.Nested(PtaPteHistorySchema()))
    pta_pte_summary = fields.Nested(PtaPteSummarySchema(), allow_none=True)
    transactions = ListField(fields.Nested(TransactionSchema()))
    correspondent = fields.Nested(CorrespondentSchema(), data_key='corr_addr')
    attorneys = ListField(fields.Nested(AttorneySchema()), data_key='attrny_addr')
    applicants = ListField(fields.Nested(ApplicantSchema()))
    inventors = ListField(fields.Nested(InventorSchema()))






