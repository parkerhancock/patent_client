import datetime
import typing as tp
from typing import Optional

from dateutil.parser import parse as parse_dt

from patent_client._async.http_client import PatentClientSession

from .model import PtabDecisionPage, PtabDocumentPage, PtabProceedingPage

client = PatentClientSession()


def convert_date(obj):
    if isinstance(obj, datetime.datetime):
        return obj.date()
    elif isinstance(obj, str):
        return parse_dt(obj).date()
    elif isinstance(obj, tuple):
        return (convert_date(o) for o in obj)


def update_query_with_date(obj, name, query_dict):
    if not obj:
        return query_dict
    obj = convert_date(obj)
    if isinstance(obj, datetime.date):
        query_dict[f"{name}Date"] = obj.isoformat()
    elif isinstance(obj, tuple):
        query_dict[f"{name}FromDate"] = obj[0].isoformat()
        query_dict[f"{name}ToDate"] = obj[1].isoformat()
    return query_dict


parameter_map = {
    "document_title": "documentTitleText",
    "style_name": "styleNameText",
    "filing_party_category": "filingPartyCategory",
    "patent_owner": "patentOwnerName",
    "party_name": "partyName",
    "document_number": "documentIdentifier",
    "document_type": "documentTypeName",
    "document_name": "documentName",
    "proceeding_number": "proceedingNumber",
    "proceeding_type": "proceedingTypeCategory",
    "application_number": "applicationNumberText",
    "start": "recordStartNumber",
    "rows": "recordTotalQuantity",
    "sort": "sortOrderCategory",
    "technology_center_number": "technologyCenterNumber",
    "inventor_name": "inventorName",
    "patent_number": "patentNumber",
    "proceeding_status": "proceedingStatusCategory",
    "subproceeding_type": "subproceedingTypeCategory",
    "decision_type": "decisionTypeCategory",
    "subdecision_type": "subdecisionTypeCategory",
    "text_search": "searchText",
}


class PtabApi:
    @classmethod
    async def get_documents(
        cls,
        document_title: Optional[tp.Optional[str]] = None,
        document_filing_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        style_name: Optional[tp.Optional[str]] = None,
        filing_party_category: Optional[tp.Optional[str]] = None,
        patent_owner_name: Optional[tp.Optional[str]] = None,
        party_name: Optional[tp.Optional[str]] = None,
        document_number: Optional[tp.Optional[str]] = None,
        document_type: Optional[tp.Optional[str]] = None,
        document_name: Optional[tp.Optional[str]] = None,
        document_identifier: Optional[tp.Optional[str]] = None,
        proceeding_number: Optional[tp.Optional[str]] = None,
        proceeding_type: Optional[tp.Optional[str]] = None,
        application_number: Optional[tp.Optional[str]] = None,
        start: Optional[tp.Optional[int]] = None,
        rows: Optional[tp.Optional[int]] = None,
        sort: Optional[tp.Union[str, tp.List[str], None]] = None,
    ) -> PtabDocumentPage:
        query_dict = {
            "documentTitleText": document_title,
            "styleNameText": style_name,
            "filingPartyCategory": filing_party_category,
            "patentOwnerName": patent_owner_name,
            "partyName": party_name,
            "documentNumber": document_number,
            "documentTypeName": document_type,
            "documentName": document_name,
            "documentIdentifier": document_identifier,
            "proceedingNumber": proceeding_number,
            "proceedingTypeCategory": proceeding_type,
            "applicationNumberText": application_number,
            "recordStartNumber": start,
            "recordTotalQuantity": rows,
            "sortOrderCategory": sort,
        }
        query_dict = {k: v for k, v in query_dict.items() if v is not None}

        query_dict = update_query_with_date(document_filing_date, "documentFiling", query_dict)

        response = await client.get(
            url="https://developer.uspto.gov/ptab-api/documents", params=query_dict
        )
        response.raise_for_status()
        return PtabDocumentPage.model_validate_json(response.content)

    @classmethod
    async def get_proceedings(
        cls,
        proceeding_number: Optional[tp.Optional[str]] = None,
        technology_center_number: Optional[tp.Optional[str]] = None,
        patent_owner: Optional[tp.Optional[str]] = None,
        party_name: Optional[tp.Optional[str]] = None,
        inventor_name: Optional[tp.Optional[str]] = None,
        patent_number: Optional[tp.Optional[str]] = None,
        declaration_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        style_name: Optional[tp.Optional[str]] = None,
        application_number: Optional[tp.Optional[str]] = None,
        proceeding_status: Optional[tp.Optional[str]] = None,
        proceeding_type: Optional[tp.Optional[str]] = None,
        subproceeding_type: Optional[tp.Optional[str]] = None,
        institution_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        proceeding_filing_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        accorded_filing_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        proceeding_last_modified_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        grant_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        start: Optional[tp.Optional[int]] = None,
        rows: Optional[tp.Optional[int]] = None,
        sort: Optional[tp.Union[str, tp.List[str], None]] = None,
    ) -> PtabDocumentPage:
        query_dict = {
            "proceedingNumber": proceeding_number,
            "technologyCenterNumber": technology_center_number,
            "patentOwnerName": patent_owner,
            "partyName": party_name,
            "inventorName": inventor_name,
            "patentNumber": patent_number,
            "styleNameText": style_name,
            "applicationNumberText": application_number,
            "proceedingStatusCategory": proceeding_status,
            "proceedingTypeCategory": proceeding_type,
            "subproceedingTypeCategory": subproceeding_type,
            "recordStartNumber": start,
            "recordTotalQuantity": rows,
            "sortOrderCategory": sort,
        }
        query_dict = {k: v for k, v in query_dict.items() if v is not None}
        query_dict = update_query_with_date(declaration_date, "declaration", query_dict)
        query_dict = update_query_with_date(institution_date, "institution", query_dict)
        query_dict = update_query_with_date(proceeding_filing_date, "proceedingFiling", query_dict)
        query_dict = update_query_with_date(accorded_filing_date, "accordedFiling", query_dict)
        query_dict = update_query_with_date(
            proceeding_last_modified_date, "proceedingLastModified", query_dict
        )
        query_dict = update_query_with_date(grant_date, "grant", query_dict)

        response = await client.get(
            url="https://developer.uspto.gov/ptab-api/proceedings", params=query_dict
        )
        response.raise_for_status()
        return PtabProceedingPage.model_validate_json(response.content)

    @classmethod
    async def get_decisions(
        cls,
        proceeding_number: Optional[tp.Optional[str]] = None,
        decision_type: Optional[tp.Optional[str]] = None,
        subdecision_type: Optional[tp.Optional[str]] = None,
        document_name: Optional[tp.Optional[str]] = None,
        decision_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        style_name: Optional[tp.Optional[str]] = None,
        proceeding_type: Optional[tp.Optional[str]] = None,
        subproceeding_type: Optional[tp.Optional[str]] = None,
        technology_center_number: Optional[tp.Optional[str]] = None,
        document_number: Optional[tp.Optional[str]] = None,
        patent_owner: Optional[tp.Optional[str]] = None,
        party_name: Optional[tp.Optional[str]] = None,
        grant_date: Optional[
            tp.Union[None, datetime.date, tuple[datetime.date], tuple[str]]
        ] = None,
        patent_number: Optional[tp.Optional[str]] = None,
        application_number: Optional[tp.Optional[str]] = None,
        text_search: Optional[tp.Optional[str]] = None,
        start: Optional[tp.Optional[int]] = None,
        rows: Optional[tp.Optional[int]] = None,
        sort: Optional[tp.Union[str, tp.List[str], None]] = None,
    ) -> PtabDocumentPage:
        query_dict = {
            "proceedingNumber": proceeding_number,
            "decisionTypeCategory": decision_type,
            "subdecisionTypeCategory": subdecision_type,
            "documentName": document_name,
            "styleNameText": style_name,
            "proceedingTypeCategory": proceeding_type,
            "subproceedingTypeCategory": subproceeding_type,
            "technologyCenterNumber": technology_center_number,
            "documentIdentifier": document_number,
            "patentOwnerName": patent_owner,
            "partyName": party_name,
            "patentNumber": patent_number,
            "applicationNumberText": application_number,
            "searchText": text_search,
            "recordStartNumber": start,
            "recordTotalQuantity": rows,
            "sortOrderCategory": sort,
        }
        query_dict = {k: v for k, v in query_dict.items() if v is not None}
        query_dict = update_query_with_date(decision_date, "decision", query_dict)
        query_dict = update_query_with_date(grant_date, "grant", query_dict)

        response = await client.get(
            url="https://developer.uspto.gov/ptab-api/decisions", params=query_dict
        )
        response.raise_for_status()
        return PtabDecisionPage.model_validate_json(response.content)
