from __future__ import annotations

import datetime
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional

from patent_client.util import Model


@dataclass
class OfficeActionRejection(Model):
    __manager__ = "patent_client.uspto.oa_rejections.manager.OfficeActionRejectionManager"
    id: Optional[str] = None
    appl_id: Optional[str] = None
    obsolete_document_identifier: Optional[str] = None
    group_art_unit: Optional[str] = None
    legacy_document_code_identifier: Optional[str] = None
    submission_date: Optional[datetime.datetime] = None
    national_class: Optional[str] = None
    national_subclass: Optional[str] = None
    header_missing: Optional[bool] = None
    form_paragraph_missing: Optional[bool] = None
    reject_form_mismatch: Optional[bool] = None
    closing_missing: Optional[bool] = None
    has_rej_101: Optional[int] = None
    has_rej_dp: Optional[int] = None
    has_rej_102: Optional[int] = None
    has_rej_103: Optional[int] = None
    has_rej_112: Optional[int] = None
    has_objection: Optional[int] = None
    cite_102_gt_1: Optional[bool] = None
    cite_103_eq_1: Optional[bool] = None
    cite_103_max: Optional[int] = None
    alice_indicator: Optional[bool] = None
    bilski_indicator: Optional[bool] = None
    mayo_indicator: Optional[bool] = None
    myriad_indicator: Optional[bool] = None
    allowed_claim_indicator: Optional[bool] = None
    signature_type: Optional[str] = None
    action_type_category: Optional[str] = None
    legal_section_code: Optional[str] = None
    paragraph_number: Optional[str] = None
    claim_number_array_document: Optional[List[str]] = field(default_factory=list)
    create_user_identifier: Optional[str] = None
    create_date_time: Optional[datetime.datetime] = None


@dataclass
class OfficeActionCitation(Model):
    __manager__ = "patent_client.uspto.oa_rejections.manager.OfficeActionCitationManager"
    id: Optional[str] = None
    appl_id: Optional[str] = None
    obsolete_document_identifier: Optional[str] = None
    reference_number: Optional[str] = None
    parsed_reference_number: Optional[str] = None
    office_action_citation_reference_indicator: Optional[bool] = None
    examiner_cited_reference_indicator: Optional[bool] = None
    applicant_cited_reference_indicator: Optional[bool] = None
    action_type_category: Optional[str] = None
    legal_section_code: Optional[str] = None
    group_art_unit: Optional[str] = None
    technology_center_number: Optional[str] = None
    work_group: Optional[str] = None
    create_user_identifier: Optional[str] = None
    create_date_time: Optional[datetime.datetime] = None


@dataclass
class OfficeActionFullText(Model):
    __manager__ = "patent_client.uspto.oa_rejections.manager.OfficeActionFullTextManager"
    id: Optional[str] = None
    obsolete_document_identifier: Optional[str] = None
    access_level_category: Optional[str] = None
    atty_docket_number: Optional[str] = None
    appl_id: Optional[str] = None
    application_type_category: Optional[str] = None
    business_area_category: Optional[str] = None
    business_entity_status_category: Optional[str] = None
    document_active_indicator: Optional[bool] = None
    examiner_employee_number: Optional[str] = None
    invention_subject_matter_category: Optional[str] = None
    invention_title: Optional[str] = None
    pct_number: Optional[str] = None
    patent_number: Optional[str] = None
    application_deemed_withdrawn_date: Optional[datetime.datetime] = None
    application_status_number: Optional[int] = None
    customer_number: Optional[str] = None
    effective_claim_total_quantity: Optional[int] = None
    effective_filing_date: Optional[datetime.datetime] = None
    figure_quantity: Optional[int] = None
    filing_date: Optional[datetime.datetime] = None
    grant_date: Optional[datetime.datetime] = None
    group_art_unit: Optional[str] = None
    independent_claim_total_quantity: Optional[int] = None
    last_modified_timestamp: Optional[datetime.datetime] = None
    nsrd_current_location_date: Optional[datetime.datetime] = None
    confirmation_number: Optional[str] = None
    submission_date: Optional[datetime.datetime] = None
    create_date_time: Optional[datetime.datetime] = None
    body_text: Optional[str] = None
