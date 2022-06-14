from gelatin_extract.json.schema import Schema
from gelatin_extract.json.schema import fields as f
from gelatin_extract.util import underscore
from patent_client.uspto.peds.schema import PtaPteHistorySchema

def inflect_keys(obj, inflector):
    if isinstance(obj, dict):
        return {inflector(k): inflect_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [inflect_keys(i) for i in obj]
    else:
        return obj

class PedsSchema(Schema):
    def pre_load(self, input_data, **kwargs):
        return inflect_keys(input_data, underscore)

class MultilineField(Combine):
    line_one = f.Str()
    line_two = f.Str()
    line_three = f.Str()
    line_four = f.Str()
    
    def __init__(self, *args, **kwargs):
        self.line_keys = [
            f"{self.name}_line_one",
            f"{self.name}_line_two",
            f"{self.name}_line_three",
            f"{self.name}_line_four",
            ]
    
    def combine_func(self, obj):
        return " ".join(obj.get(lk, '') for lk in self.line_keys)


class InventorSchema(PedsSchema):
    name = MultilineField()
    street = MultilineField()
    city = f.Str()
    geo_code = f.Str()
    postal_code = f.Str()
    rank_no = f.Int()

class ApplicantSchema(InventorSchema):
    cust_no = f.Str()

class TransactionSchema(PedsSchema):
    date = f.Date()
    code = f.Str()
    description = f.Str()

class ChildSchema(PedsSchema):
    parent_appl_id = f.Str('application_number_text')
    child_appl_id = f.Str('claim_application_number_text')
    relationship = f.Str('application_status_description',
        formatter=lambda x: x.replace('This application ', ''))

class ParentSchema(PedsSchema):
    parent_appl_id = f.Str('claim_application_number_text')
    child_appl_id = f.Str('application_number_text')
    relationship = f.Str('application_status_description',
        formatter=lambda x: x.replace('This application ', ''))

class PtaPteHistorySchema(PedsSchema):
    date = f.Date("pta_or_pte_date")
    description = f.String("contents_description")
    

class USApplicationSchema(PedsSchema):
    # Basic Bibliographic Data
    appl_id = f.Str()
    app_confr_number = f.Str()
    app_filing_date = f.Str()
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
    child_continuity: List[Child]
    parent_continuity: List[Parent]
    pta_pte_tran_history: List[PtaPteHistory]
    pta_pte_summary: PtaPteSummary
    correspondent: Correspondent
    attorneys: List[Attorney]
    foreign_priority: List[ForeignPriority]