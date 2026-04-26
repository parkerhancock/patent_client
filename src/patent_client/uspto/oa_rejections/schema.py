import datetime

from dateutil.parser import ParserError
from dateutil.parser._parser import ParserError
from yankee.json.schema import fields as f
from yankee.json.schema import Schema


signature_types = {
    0: "Examiner",
    1: "Primary Examiner",
    2: "Examiner + Primary Examiner",
    3: "Examiner + Supervisory Patent Examiner",
    4: "Examiner + PE/SPE + Director",
}


class FlexibleIntField(f.Field):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        if obj is None:
            return None
        try:
            return int(float(obj))
        except ValueError:
            return 0


class FlexibleDateTimeField(f.DateTime):
    def deserialize(self, obj):
        try:
            return super().deserialize(obj)
        except ParserError:
            return datetime.date(1900, 1, 1)


class BoolField(FlexibleIntField):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return obj == 1


class SignatureField(FlexibleIntField):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return signature_types[obj]


class OfficeActionRejectionSchema(Schema):
    id = f.Str()
    appl_id = f.Str(data_key="patentApplicationNumber")
    obsolete_document_identifier = f.Str()
    group_art_unit = f.Str("groupArtUnitNumber")
    legacy_document_code_identifier = f.Str()
    submission_date = FlexibleDateTimeField()
    national_class = f.Str()
    national_subclass = f.Str()
    header_missing = BoolField()
    form_paragraph_missing = BoolField()
    reject_form_mismatch = BoolField()
    closing_missing = BoolField()
    has_rej_101 = FlexibleIntField()
    has_rej_DP = FlexibleIntField()
    has_rej_102 = FlexibleIntField()
    has_rej_103 = FlexibleIntField()
    has_rej_112 = FlexibleIntField()
    has_objection = FlexibleIntField()
    cite_102_GT1 = BoolField()
    cite_103_EQ1 = BoolField()
    cite_103_max = FlexibleIntField()
    alice_indicator = BoolField()
    bilski_indicator = BoolField()
    mayo_indicator = BoolField()
    myriad_indicator = BoolField()
    allowed_claim_indicator = BoolField()
    signature_type = SignatureField()
    action_type_category = f.Str()
    legal_section_code = f.Str()
    paragraph_number = f.Str()
    claim_number_array_document = f.List(f.Str(), data_key="claimNumberArrayDocument")
    create_user_identifier = f.Str()
    create_date_time = FlexibleDateTimeField()


class OfficeActionCitationSchema(Schema):
    id = f.Str()
    appl_id = f.Str(data_key="patentApplicationNumber")
    obsolete_document_identifier = f.Str()
    reference_number = f.Str()
    parsed_reference_number = f.Str()
    office_action_citation_reference_indicator = f.Bool()
    examiner_cited_reference_indicator = f.Bool()
    applicant_cited_reference_indicator = f.Bool()
    action_type_category = f.Str()
    legal_section_code = f.Str()
    group_art_unit = f.Str("groupArtUnitNumber")
    technology_center_number = f.Str("techCenter")
    work_group = f.Str()
    create_user_identifier = f.Str()
    create_date_time = FlexibleDateTimeField()


class OfficeActionFullTextSchema(Schema):
    id = f.Str()
    obsolete_document_identifier = f.Str("obsoleteDocumentIdentifier.0")
    access_level_category = f.Str("accessLevelCategory.0")
    atty_docket_number = f.Str("applicantFileReference.0")
    appl_id = f.Str(data_key="patentApplicationNumber.0")
    application_type_category = f.Str("applicationTypeCategory.0")
    business_area_category = f.Str("businessAreaCategory.0")
    business_entity_status_category = f.Str("businessEntityStatusCategory.0")
    document_active_indicator = f.Bool("documentActiveIndicator.0", true_value="1")
    examiner_employee_number = f.Str("examinerEmployeeNumber.0")
    invention_subject_matter_category = f.Str("inventionSubjectMatterCategory.0")
    invention_title = f.Str("inventionTitle.0")
    pct_number = f.Str("patentApplicationPatentCooperationTreatyNumber.0")
    patent_number = f.Str("patentNumber.0")
    application_deemed_withdrawn_date = FlexibleDateTimeField()
    application_status_number = FlexibleIntField()
    customer_number = f.Str()
    effective_claim_total_quantity = FlexibleIntField()
    effective_filing_date = FlexibleDateTimeField()
    figure_quantity = FlexibleIntField()
    filing_date = FlexibleDateTimeField()
    grant_date = FlexibleDateTimeField()
    group_art_unit = f.Str("groupArtUnitNumber")
    independent_claim_total_quantity = FlexibleIntField()
    last_modified_timestamp = FlexibleDateTimeField()
    nsrd_current_location_date = FlexibleDateTimeField("nSRDCurrentLocationDate")
    confirmation_number = f.Str("patentApplicationConfirmationNumber")
    submission_date = FlexibleDateTimeField()
    create_date_time = FlexibleDateTimeField()
    body_text = f.Str("bodyText.0")


class OfficeActionRejectionPageSchema(Schema):
    num_found = FlexibleIntField(data_key="response.numFound")
    docs = f.List(OfficeActionRejectionSchema, data_key="response.docs")


class OfficeActionCitationPageSchema(Schema):
    num_found = FlexibleIntField(data_key="response.numFound")
    docs = f.List(OfficeActionCitationSchema, data_key="response.docs")


class OfficeActionFulltextPageSchema(Schema):
    num_found = FlexibleIntField(data_key="response.numFound")
    docs = f.List(OfficeActionFullTextSchema, data_key="response.docs")
