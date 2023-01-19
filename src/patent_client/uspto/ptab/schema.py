from yankee.json import fields as f
from yankee.json import Schema


class AdditionalRespondentSchema(Schema):
    application_number_text = f.Str()
    inventor_name = f.Str()
    patent_number = f.Str()
    party_name = f.Str()


class PtabProceedingSchema(Schema):
    # Proceeding Metadata
    last_modified_date = f.DateTime()
    last_modified_user_id = f.DateTime()
    institution_decision_date = f.Date()
    proceeding_filing_date = f.Date()
    accorded_filing_date = f.Date()
    proceeding_status_category = f.Str()
    proceeding_number = f.Str()
    proceeding_last_modified_date = f.Date()
    proceeding_type_category = f.Str()
    subproceeding_type_category = f.Str()
    decision_date = f.Date()
    docket_notice_mail_date = f.Date()
    declaration_date = f.Date()
    style_name_text = f.Str()

    # Respondent Information
    respondent_technology_center_number = f.Str()
    respondent_patent_owner_name = f.Str()
    respondent_party_name = f.Str()
    respondent_group_art_unit_number = f.Str()
    respondent_inventor_name = f.Str()
    respondent_counsel_name = f.Str()
    respondent_grant_date = f.Date()
    respondent_patent_number = f.Str()
    respondent_application_number_text = f.Str()
    respondent_publication_number = f.Str()
    respondent_publication_date = f.Date()

    # Petitioner Information
    petitioner_technology_center_number = f.Str()
    petitioner_patent_owner_name = f.Str()
    petitioner_party_name = f.Str()
    petitioner_group_art_unit_number = f.Str()
    petitioner_inventor_name = f.Str()
    petitioner_counsel_name = f.Str()
    petitioner_grant_date = f.Date()
    petitioner_patent_number = f.Str()
    petitioner_application_number_text = f.Str()

    # Appellant Information
    appellant_technology_center_number = f.Str()
    appellant_patent_owner_name = f.Str()
    appellant_party_name = f.Str()
    appellant_group_art_unit_number = f.Str()
    appellant_inventor_name = f.Str()
    appellant_counsel_name = f.Str()
    appellant_grant_date = f.Date()
    appellant_patent_number = f.Str()
    appellant_application_number_text = f.Str()
    appellant_publication_date = f.Date()
    appellant_publication_number = f.Str()
    third_party_name = f.Str()

    # Second Respondent (if any)
    second_respondent_party_name = f.Str()
    second_respondent_appl_number_text = f.Str()
    second_respondent_patent_number = f.Str()
    second_respondent_grant_date = f.Date()
    second_respondent_patent_owner_name = f.Str()
    second_respondent_inventor_name = f.Str()
    second_respondent_counsel_name = f.Str()
    second_respondent_g_a_u_number = f.Str()
    second_respondent_tech_center_number = f.Str()
    second_respondent_pub_number = f.Str()
    second_respondent_publication_date = f.Date()

    additional_respondents = f.List(AdditionalRespondentSchema, data_key="additionalRespondentPartyDataBag")


class PtabDocumentSchema(Schema):
    document_identifier = f.Str()
    document_category = f.Str()
    document_type_name = f.Str()
    document_number = f.Int()
    document_name = f.Str()
    document_filing_date = f.Date()
    document_title = f.Str()
    proceeding_number = f.Str()
    proceeding_type_category = f.Str()


class PtabDecisionSchema(Schema):
    proceeding_number = f.Str()
    board_rulings = f.List(f.Str())
    decision_type_category = f.Str()
    document_identifier = f.Str()
    document_name = f.Str()
    identifier = f.Str()
    issue_type = f.List(f.Str())
    object_uu_id = f.Str()
    petitioner_technology_center_number = f.Str()
    subdecision_type_category = f.Str()
