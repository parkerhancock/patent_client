from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    date_range_data: Optional[Dict[str, Dict[str, str]]] = Field(
        None, serialization_alias="dateRangeData"
    )
    parameter_data: Optional[Dict[str, str]] = Field(None, serialization_alias="parameterData")
    facet_data: Optional[Dict[str, List[Dict[str, Optional[str]]]]] = Field(
        None, serialization_alias="facetData"
    )
    record_start_number: Optional[int] = Field(None, serialization_alias="recordStartNumber")
    record_total_quantity: Optional[int] = Field(None, serialization_alias="recordTotalQuantity")
    sort_data_bag: Optional[List[Dict[str, str]]] = Field(None, serialization_alias="sortDataBag")
    search_text: Optional[str] = Field(None, serialization_alias="searchText")
    action_download: Optional[bool] = Field(None, serialization_alias="actionDownload")

    def __repr__(self) -> str:
        return (
            f"SearchInput(date_range_data={self.date_range_data!r}, parameter_data={self.parameter_data!r}, "
            f"facet_data={self.facet_data!r}, record_start_number={self.record_start_number!r}, "
            f"record_total_quantity={self.record_total_quantity!r}, sort_data_bag={self.sort_data_bag!r}, "
            f"search_text={self.search_text!r}, action_download={self.action_download!r})"
        )


class ProceedingsGetParams(BaseModel):
    proceeding_number: Optional[str] = None
    technology_center_number: Optional[str] = None
    patent_owner_name: Optional[str] = None
    party_name: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_number: Optional[str] = None
    declaration_date: Optional[date] = None
    declaration_from_date: Optional[date] = None
    declaration_to_date: Optional[date] = None
    style_name_text: Optional[str] = None
    application_number_text: Optional[str] = None
    proceeding_status_category: Optional[str] = None
    proceeding_type_category: Optional[str] = None
    subproceeding_type_category: Optional[str] = None
    institution_decision_date: Optional[date] = None
    institution_decision_from_date: Optional[date] = None
    institution_decision_to_date: Optional[date] = None
    proceeding_filing_date: Optional[date] = None
    proceeding_filing_from_date: Optional[date] = None
    proceeding_filing_to_date: Optional[date] = None
    accorded_filing_date: Optional[date] = None
    accorded_filing_from_date: Optional[date] = None
    accorded_filing_to_date: Optional[date] = None
    proceeding_last_modified_date: Optional[date] = None
    proceeding_last_modified_from_date: Optional[date] = None
    proceeding_last_modified_to_date: Optional[date] = None
    grant_date: Optional[date] = None
    grant_from_date: Optional[date] = None
    grant_to_date: Optional[date] = None
    record_total_quantity: Optional[int] = None
    record_start_number: Optional[int] = None
    sort_order_category: Optional[str] = None


class DocumentsGetParams(BaseModel):
    document_title_text: Optional[str] = None
    document_filing_date: Optional[date] = None
    document_filing_from_date: Optional[date] = None
    document_filing_to_date: Optional[date] = None
    style_name_text: Optional[str] = None
    filing_party_category: Optional[str] = None
    patent_owner_name: Optional[str] = None
    party_name: Optional[str] = None
    document_number: Optional[str] = None
    document_type_name: Optional[str] = None
    document_name: Optional[str] = None
    document_identifier: Optional[str] = None
    proceeding_number: Optional[str] = None
    proceeding_type_category: Optional[str] = None
    application_number_text: Optional[str] = None
    record_total_quantity: int
    record_start_number: Optional[int] = None
    sort_order_category: Optional[str] = None


class DecisionsGetParams(BaseModel):
    proceeding_number: Optional[str] = None
    decision_type_category: Optional[str] = None
    subdecision_type_category: Optional[str] = None
    document_name: Optional[str] = None
    proceeding_type_category: Optional[str] = None
    subproceeding_type_category: Optional[str] = None
    document_identifier: Optional[str] = None
    technology_center_number: Optional[str] = None
    patent_owner_name: Optional[str] = None
    party_name: Optional[str] = None
    inventor_name: Optional[str] = None
    patent_number: Optional[str] = None
    decision_date: Optional[date] = None
    decision_from_date: Optional[date] = None
    decision_to_date: Optional[date] = None
    style_name_text: Optional[str] = None
    application_number_text: Optional[str] = None
    search_text: Optional[str] = None
    record_total_quantity: int
    record_start_number: Optional[int] = None
    sort_order_category: Optional[str] = None


class ProceedingAggregationDataParams(BaseModel):
    proceeding_filing_from_date: str
    proceeding_filing_to_date: str
