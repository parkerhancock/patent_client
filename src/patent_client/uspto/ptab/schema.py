import inflection
from marshmallow import EXCLUDE
from marshmallow import Schema
from marshmallow import ValidationError
from marshmallow import fields
from marshmallow import post_load
from marshmallow import pre_load

from patent_client.util import ListField

from .model import PtabDecision
from .model import PtabDocument
from .model import PtabProceeding
from .util import conversions


def create_subset(data, name, keys):
    subset = {k: data.pop(k) for k in keys if k in data}
    if subset:
        data[name] = subset
    return data


def create_subset_from_prefix(data, prefix):
    keys = [k for k in data.keys() if k.startswith(prefix)]
    return create_subset(data, prefix, keys)


class BaseSchema(Schema):
    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data = {inflection.underscore(k): v for k, v in input_data.items()}
        for k, v in conversions.items():
            if k in input_data:
                input_data[conversions[k]] = input_data.pop(k)
        return input_data

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class PtabProceedingSchema(BaseSchema):
    __model__ = PtabProceeding
    appl_id = fields.Str(data_key="respondent_application_number_text")
    patent_number = fields.Str(data_key="respondent_patent_number")
    accorded_filing_date = fields.Date()
    decision_date = fields.Date()
    institution_decision_date = fields.Date()
    proceeding_filing_date = fields.Date()
    respondent_grant_date = fields.Date()
    respondent_party_name = fields.Str(allow_none=True)

    class Meta:
        unknown = EXCLUDE
        dateformat = "%m-%d-%Y"
        additional = (
            "subproceeding_type_category",
            "proceeding_number",
            "proceeding_status_category",
            "proceeding_type_category",
            # Party Information
            "petitioner_counsel_name",
            "petitioner_party_name",
            "respondent_counsel_name",
            "respondent_patent_owner_name",
            # Application Information
            "inventor",
            "patent_number",
            "respondent_technology_center_number",
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
    board_rulings = ListField(fields.Str())
    decision_type_category = fields.Str()
    document_identifier = fields.Str()
    document_name = fields.Str()
    identifier = fields.Str()
    issue_type = ListField(fields.Str())
    object_uu_id = fields.Str()
    petitioner_technology_center_number = fields.Str()
    subdecision_type_category = fields.Str()

    class Meta:
        unknown = EXCLUDE
        dateformat = "%m-%d-%Y"
