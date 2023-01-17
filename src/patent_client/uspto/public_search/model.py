import datetime
from dataclasses import dataclass, field
from patent_client.util.base.model import Model, ListManager

@dataclass
class PatentBiblio(Model):
    abstract_end:int = None
    abstract_start:int = None
    amend_end:int = None
    amend_start:int = None
    applicant_name: "ListManager[str]" = field(default_factory=ListManager)
    application_filing_date: "ListManager[datetime.date]" = field(default_factory=ListManager)
    application_number:str = None
    assignee_name: "ListManager[str]" = field(default_factory=ListManager)
    assistant_examiner: "ListManager[str]" = field(default_factory=ListManager)
    bib_end:int = None
    bib_start:int = None
    cert_correction_end:int = None
    cert_correction_start:int = None
    cert_reexamination_end:int = None
    cert_reexamination_start:int = None
    claims_end:int = None
    claims_start:int = None
    composite_id:str = None
    cpc_additional_flattened:str = None
    cpc_inventive_flattened:str = None
    database_name:str = None
    date_published:datetime.date = None
    description_end:int = None
    description_start:int = None
    document_id:str = None
    document_size:int = None
    drawings_end:int = None
    drawings_start:int = None
    family_identifier_cur:int = None
    front_page_end:int = None
    front_page_start:int = None
    government_interest: "ListManager[str]" = field(default_factory=ListManager)
    guid:str = None
    image_file_name:str = None
    image_location:str = None
    invention_title:str = None
    inventors_short:str = None
    ipc_code_flattened:str = None
    kind_code: "ListManager[str]" = field(default_factory=ListManager)
    language_indicator:str = None
    main_classification_code:str = None
    page_count:int = None
    page_count_display:str = None
    previously_viewed:bool = None
    primary_examiner:str = None
    ptab_end:int = None
    ptab_start:int = None
    publication_reference_document_number:str = None
    publication_reference_document_number_1:str = None
    publication_reference_document_number_one:str = None
    related_appl_filing_date: "ListManager[datetime.date]" = field(default_factory=ListManager)
    score:float = None
    search_report_end:int = None
    search_report_start:int = None
    specification_end:int = None
    specification_start:int = None
    supplemental_end:int = None
    supplemental_start:int = None
    type:str = None
    unused:bool = None
    urpn: "ListManager[str]" = field(default_factory=ListManager)
    urpn_code: "ListManager[str]" = field(default_factory=ListManager)
    uspc_full_classification_flattened:str = None

@dataclass
class PatentDocument(Model):
    abstract_end:int = None
    abstract_html:str = None
    abstract_start:int = None
    amend_end:int = None
    amend_start:int = None
    applicant_authority_type: "ListManager[str]" = field(default_factory=ListManager)
    applicant_city: "ListManager[str]" = field(default_factory=ListManager)
    applicant_country: "ListManager[str]" = field(default_factory=ListManager)
    applicant_group: "ListManager[str]" = field(default_factory=ListManager)
    applicant_name: "ListManager[str]" = field(default_factory=ListManager)
    applicant_state: "ListManager[str]" = field(default_factory=ListManager)
    applicant_zip_code: "ListManager[str]" = field(default_factory=ListManager)
    application_filing_date: "ListManager[datetime.date]" = field(default_factory=ListManager)
    application_filing_date_int:int = None
    application_kind_code:str = None
    application_number:str = None
    application_number_highlights: "ListManager[str]" = field(default_factory=ListManager)
    application_ref_filing_type:str = None
    application_serial_number: "ListManager[str]" = field(default_factory=ListManager)
    application_series_and_number:str = None
    application_series_code:str = None
    application_year:str = None
    application_year_search:str = None
    assignee_1:str = None
    assignee_city: "ListManager[str]" = field(default_factory=ListManager)
    assignee_country: "ListManager[str]" = field(default_factory=ListManager)
    assignee_name: "ListManager[str]" = field(default_factory=ListManager)
    assignee_postal_code: "ListManager[str]" = field(default_factory=ListManager)
    assignee_state: "ListManager[str]" = field(default_factory=ListManager)
    assignee_type_code: "ListManager[str]" = field(default_factory=ListManager)
    assistant_examiner: "ListManager[str]" = field(default_factory=ListManager)
    attorney_name: "ListManager[str]" = field(default_factory=ListManager)
    background_text_html:str = None
    bib_end:int = None
    bib_start:int = None
    brief_html:str = None
    cert_correction_end:int = None
    cert_correction_start:int = None
    cert_of_correction_flag:str = None
    cert_reexamination_end:int = None
    cert_reexamination_start:int = None
    claim_statement:str = None
    claims_end:int = None
    claims_html:str = None
    claims_start:int = None
    composite_id:str = None
    continuity_data: "ListManager[str]" = field(default_factory=ListManager)
    country:str = None
    cpc_additional: "ListManager[str]" = field(default_factory=ListManager)
    cpc_additional_flattened:str = None
    cpc_combination_classification_cur: "ListManager[str]" = field(default_factory=ListManager)
    cpc_combination_sets_cur_highlights: "ListManager[str]" = field(default_factory=ListManager)
    cpc_combination_tally_cur: "ListManager[str]" = field(default_factory=ListManager)
    cpc_cur_additional_class: "ListManager[str]" = field(default_factory=ListManager)
    cpc_cur_classification_group: "ListManager[str]" = field(default_factory=ListManager)
    cpc_cur_inventive_class: "ListManager[str]" = field(default_factory=ListManager)
    cpc_inventive: "ListManager[str]" = field(default_factory=ListManager)
    cpc_inventive_flattened:str = None
    cpc_orig_additional_classification: "ListManager[str]" = field(default_factory=ListManager)
    cpc_orig_classification_group: "ListManager[str]" = field(default_factory=ListManager)
    cpc_orig_inventive_classification_highlights: "ListManager[str]" = field(default_factory=ListManager)
    cpc_orig_inventv_clssif_hlghts: "ListManager[str]" = field(default_factory=ListManager)
    cur_cpc_classification_full: "ListManager[str]" = field(default_factory=ListManager)
    cur_cpc_subclass_full: "ListManager[str]" = field(default_factory=ListManager)
    cur_intl_patent_classification_noninvention: "ListManager[str]" = field(default_factory=ListManager)
    cur_intl_patent_classification_primary: "ListManager[str]" = field(default_factory=ListManager)
    cur_intl_patent_classification_secondary: "ListManager[str]" = field(default_factory=ListManager)
    cur_us_classification_us_primary_class:str = None
    current_us_cross_reference_classification: "ListManager[str]" = field(default_factory=ListManager)
    current_us_original_classification:str = None
    current_us_patent_class: "ListManager[str]" = field(default_factory=ListManager)
    database_name:str = None
    date_produced:datetime.date = None
    date_publ_search:datetime.date = None
    date_publ_year:str = None
    date_publ_year_search:str = None
    date_published:datetime.date = None
    derwent_week_int:int = None
    description_end:int = None
    description_html:str = None
    description_start:int = None
    document_id:str = None
    document_size:int = None
    drawings_end:int = None
    drawings_start:int = None
    examiner_group:str = None
    exemplary_claim_number: "ListManager[str]" = field(default_factory=ListManager)
    family_identifier_cur:int = None
    family_identifier_cur_str:str = None
    field_of_search_class_subclass_highlights: "ListManager[str]" = field(default_factory=ListManager)
    field_of_search_cpc_classification: "ListManager[str]" = field(default_factory=ListManager)
    field_of_search_cpc_main_class: "ListManager[str]" = field(default_factory=ListManager)
    field_of_search_main_class_national: "ListManager[str]" = field(default_factory=ListManager)
    field_of_search_subclasses: "ListManager[str]" = field(default_factory=ListManager)
    foreign_ref_citation_classification: "ListManager[str]" = field(default_factory=ListManager)
    foreign_ref_citation_cpc: "ListManager[str]" = field(default_factory=ListManager)
    foreign_ref_country_code: "ListManager[str]" = field(default_factory=ListManager)
    foreign_ref_group: "ListManager[str]" = field(default_factory=ListManager)
    foreign_ref_patent_number: "ListManager[str]" = field(default_factory=ListManager)
    foreign_ref_pub_date: "ListManager[str]" = field(default_factory=ListManager)
    foreign_ref_pub_date_kwic_hits: "ListManager[str]" = field(default_factory=ListManager)
    front_page_end:int = None
    front_page_start:int = None
    government_interest: "ListManager[str]" = field(default_factory=ListManager)
    guid:str = None
    ice_xml_indicator:str = None
    id_without_solr_partition:str = None
    image_file_name:str = None
    image_location:str = None
    intl_further_classification: "ListManager[str]" = field(default_factory=ListManager)
    intl_pub_classification_class: "ListManager[str]" = field(default_factory=ListManager)
    intl_pub_classification_group: "ListManager[str]" = field(default_factory=ListManager)
    intl_pub_classification_non_invention: "ListManager[str]" = field(default_factory=ListManager)
    intl_pub_classification_primary: "ListManager[str]" = field(default_factory=ListManager)
    intl_pub_classification_secondary: "ListManager[str]" = field(default_factory=ListManager)
    invention_title:str = None
    inventor_city: "ListManager[str]" = field(default_factory=ListManager)
    inventor_country: "ListManager[str]" = field(default_factory=ListManager)
    inventor_postal_code: "ListManager[str]" = field(default_factory=ListManager)
    inventor_state: "ListManager[str]" = field(default_factory=ListManager)
    inventors_name: "ListManager[str]" = field(default_factory=ListManager)
    inventors_short:str = None
    ipc_all_main_classification: "ListManager[str]" = field(default_factory=ListManager)
    ipc_code_flattened:str = None
    kind_code: "ListManager[str]" = field(default_factory=ListManager)
    language_indicator:str = None
    legal_firm_name: "ListManager[str]" = field(default_factory=ListManager)
    legal_representative_country:str = None
    main_classification_code:str = None
    number_of_claims:str = None
    number_of_drawing_sheets:str = None
    number_of_figures:str = None
    object_contents:str = None
    object_description:str = None
    other_ref_pub: "ListManager[str]" = field(default_factory=ListManager)
    page_count:int = None
    page_count_display:str = None
    previously_viewed:bool = None
    primary_examiner:str = None
    primary_examiner_highlights:str = None
    principal_attorney_name: "ListManager[str]" = field(default_factory=ListManager)
    ptab_end:int = None
    ptab_start:int = None
    pub_ref_country_code:str = None
    pub_ref_doc_number:str = None
    pub_ref_doc_number_1:str = None
    publication_reference_document_number:str = None
    publication_reference_document_number_1:str = None
    publication_reference_document_number_one:str = None
    query_id:int = None
    related_appl_child_patent_country: "ListManager[str]" = field(default_factory=ListManager)
    related_appl_child_patent_number: "ListManager[str]" = field(default_factory=ListManager)
    related_appl_country_code: "ListManager[str]" = field(default_factory=ListManager)
    related_appl_filing_date: "ListManager[datetime.date]" = field(default_factory=ListManager)
    related_appl_number: "ListManager[str]" = field(default_factory=ListManager)
    related_appl_parent_status_code: "ListManager[str]" = field(default_factory=ListManager)
    related_appl_patent_issue_date: "ListManager[datetime.date]" = field(default_factory=ListManager)
    related_appl_patent_number: "ListManager[str]" = field(default_factory=ListManager)
    score:float = None
    search_report_end:int = None
    search_report_start:int = None
    specification_end:int = None
    specification_start:int = None
    supplemental_end:int = None
    supplemental_start:int = None
    term_of_extension:str = None
    type:str = None
    unused:bool = None
    urpn: "ListManager[str]" = field(default_factory=ListManager)
    urpn_code: "ListManager[str]" = field(default_factory=ListManager)
    us_ref_classification: "ListManager[str]" = field(default_factory=ListManager)
    us_ref_cpc_classification: "ListManager[str]" = field(default_factory=ListManager)
    us_ref_group: "ListManager[str]" = field(default_factory=ListManager)
    us_ref_issue_date: "ListManager[str]" = field(default_factory=ListManager)
    us_ref_issue_date_kwic_hits: "ListManager[str]" = field(default_factory=ListManager)
    us_ref_patentee_name: "ListManager[str]" = field(default_factory=ListManager)
    uspc_full_classification_flattened:str = None
