from marshmallow import Schema, fields, EXCLUDE, pre_load, post_load, ValidationError
from .model import PtabProceeding, PtabDocument, PtabDecision
import inflection

class BaseSchema(Schema):
    @pre_load
    def pre_load(self, input_data, **kwargs):
        print(input_data)
        return {inflection.underscore(k): v for k, v in input_data.items()}

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)

class PtabProceedingSchema(BaseSchema):
    __model__ = PtabProceeding
    accorded_filing_date = fields.Date()
    decision_date = fields.Date()
    institution_decision_date = fields.Date()
    proceeding_filing_date = fields.Date()
    respondent_grant_date = fields.Date()

    class Meta:
        unknown = EXCLUDE
        dateformat = "%m-%d-%Y"
        additional = (
            'subproceeding_type_category',
            'proceeding_number',
            'proceeding_status_category',
            'proceeding_type_category',
            
            # Party Information
            'petitioner_counsel_name',
            'petitioner_party_name',
            'respondent_counsel_name',
            'respondent_party_name',
            'respondent_patent_owner_name',

            # Application Information
            'respondent_application_number_text',
            'respondent_inventor_name',
            'respondent_patent_number',
            'respondent_technology_center_number',
        )

class PtabDocumentSchema(BaseSchema):
    __model__ = PtabDocument
    document_identifier = fields.Str()
    document_category = fields.Str()
    document_type_name = fields.Str()
    document_number = fields.Int()
    document_name = fields.Str()
    document_filing_date = fields.Date()
    document_title = fields.Str()
    proceeding_number = fields.Str()
    proceeding_type_category = fields.Str()
    
    class Meta:
        unknown = EXCLUDE
        dateformat = "%m-%d-%Y"

class PtabDecisionSchema(BaseSchema):
    __model__ = PtabDecision
    proceeding_number = fields.Str()
    board_rulings = fields.List(fields.Str())
    decision_type_category = fields.Str()
    document_identifier = fields.Str()
    document_name = fields.Str()
    identifier = fields.Str()
    issue_type = fields.List(fields.Str())
    object_uu_id = fields.Str()
    petitioner_technology_center_number = fields.Str()
    subdecision_type_category = fields.Str()

    class Meta:
        unknown = EXCLUDE
        dateformat = "%m-%d-%Y"