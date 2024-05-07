import datetime
import json
from pathlib import Path

import pytest

from .model import (
    AssigneeAddress,
    Assignment,
    Continuity,
    CustomerNumber,
    Document,
    ForeignPriority,
    SearchRequest,
    TermAdjustment,
    TermAdjustmentHistory,
    Transaction,
    USApplication,
    USApplicationBiblio,
)


@pytest.fixture
def fixture_dir():
    return Path(__file__).parent / "fixtures"


def test_continuity(fixture_dir):
    data = json.loads((fixture_dir / "continuity.json").read_text())
    continuity = Continuity(**data)
    assert continuity.count == 1
    assert continuity.request_identifier == "50b0e4d5-98f0-4f5a-a550-5c45a9a52109"
    assert len(continuity.parent_continuity) == 2
    assert continuity.parent_continuity[0].application_status_code == 161
    assert continuity.parent_continuity[0].claim_type_code == "NST"
    assert continuity.parent_continuity[0].filing_date == datetime.date(2015, 4, 22)
    assert (
        continuity.parent_continuity[0].application_status_description
        == "Abandoned  --  Failure to Respond to an Office Action"
    )
    assert continuity.parent_continuity[0].claim_type_description == "is a National Stage Entry of"
    assert continuity.parent_continuity[0].parent_application_id == "PCT/US15/27322"
    assert continuity.parent_continuity[0].child_application_id == "15123456"
    assert len(continuity.child_continuity) == 1
    assert continuity.child_continuity[0].application_status_code == 160
    assert continuity.child_continuity[0].claim_type_code == "CON"
    assert continuity.child_continuity[0].filing_date == datetime.date(2018, 9, 13)
    assert (
        continuity.child_continuity[0].application_status_description
        == "Abandoned  --  Incomplete Application (Pre-examination)"
    )
    assert continuity.child_continuity[0].claim_type_description == "is a Continuation of"
    assert continuity.child_continuity[0].parent_application_id == "15123456"
    assert continuity.child_continuity[0].child_application_id == "16132008"


def test_document(fixture_dir):
    data = json.loads((fixture_dir / "documents.json").read_text())
    for doc_data in data["documentBag"]:
        document = Document(**doc_data)
        assert document.appl_id == "16330077"
        assert isinstance(document.mail_date, datetime.datetime)
        assert document.document_identifier is not None
        assert document.document_code is not None
        assert document.document_code_description is not None
        assert document.direction_category in ["INCOMING", "OUTGOING", "INTERNAL"]
        assert isinstance(document.download_option_bag, list)
        for download_option in document.download_option_bag:
            assert download_option["mimeTypeIdentifier"] in ["PDF", "XML", "MS_WORD"]
            assert download_option["downloadUrl"].startswith(
                "https://beta-api.uspto.gov/api/v1/download/applications/16330077/"
            )
            assert isinstance(download_option["pageTotalQuantity"], int)


def test_assignment(fixture_dir):
    data = json.loads((fixture_dir / "assignment.json").read_text())
    assignment_bag = data["patentBag"][0]["assignmentBag"]
    for assignment_data in assignment_bag:
        assignment = Assignment(**assignment_data)
        assert isinstance(assignment.assignment_received_date, datetime.date)
        assert isinstance(assignment.assignment_recorded_date, datetime.date)
        assert isinstance(assignment.assignment_mailed_date, datetime.date)
        assert assignment.frame_number is not None
        assert assignment.page_number > 0
        assert assignment.reel_number_frame_number is not None
        assert assignment.reel_number is not None
        assert assignment.conveyance_text is not None
        for assignor in assignment.assignor_bag:
            assert isinstance(assignor.execution_date, datetime.date)
            assert assignor.assignor_name is not None
        for assignee in assignment.assignee_bag:
            assert assignee.assignee_name_text is not None
            assert isinstance(assignee.assignee_address, AssigneeAddress)
            assert assignee.assignee_address.city_name is not None
            assert assignee.assignee_address.geographic_region_code is not None
            assert assignee.assignee_address.postal_code is not None
            assert assignee.assignee_address.address_line_one_text is not None
        for correspondence in assignment.correspondence_address:
            assert correspondence.address_line_one_text is not None
            assert correspondence.address_line_two_text is not None
            assert correspondence.correspondent_name_text is not None


def test_foreign_priority(fixture_dir):
    data = json.loads((fixture_dir / "foreign_priority.json").read_text())
    foreign_priority_bag = data["patentBag"][0]["foreignPriorityBag"]
    for foreign_priority_data in foreign_priority_bag:
        foreign_priority = ForeignPriority(**foreign_priority_data)
        assert foreign_priority.priority_number_text is not None
        assert isinstance(foreign_priority.filing_date, datetime.date)
        assert foreign_priority.country_name is not None


def test_attorney(fixture_dir):
    data = json.loads((fixture_dir / "attorney.json").read_text())
    customer_number = CustomerNumber(**data["patentBag"][0]["recordAttorney"])
    assert customer_number.customer_number == "26161.0000000000"
    assert len(customer_number.attorneys) > 0
    for attorney in customer_number.attorneys:
        assert attorney.active_indicator in ["ACTIVE", "INACTIVE"]
        assert attorney.first_name is not None
        assert attorney.last_name is not None
        assert attorney.registration_number is not None
        assert len(attorney.attorney_address_bag) > 0
        assert len(attorney.telecommunication_address_bag) > 0
        for telecom in attorney.telecommunication_address_bag:
            assert telecom.telecommunication_number is not None
            assert telecom.usage_type_category in ["FAX", "TEL", "EMAIL"]
    assert customer_number.address is not None
    assert customer_number.address.city_name == "MINNEAPOLIS"
    assert customer_number.address.geographic_region_code == "MN"
    assert customer_number.address.country_code == "US"
    assert customer_number.address.postal_code == "55440-1022"
    assert customer_number.address.country_name == "UNITED STATES"
    assert customer_number.address.address_line_one_text == "P.O. BOX 1022"


def test_transactions(fixture_dir):
    data = json.loads((fixture_dir / "transactions.json").read_text())
    transactions = [
        Transaction(**transaction_data)
        for transaction_data in data["patentBag"][0]["transactionContentBag"]
    ]
    for transaction in transactions:
        assert transaction.recorded_date is not None
        assert transaction.transaction_code is not None
        assert transaction.transaction_description is not None
        # Test for specific transaction details based on the provided fixtures
    assert transactions[0].recorded_date == datetime.date.fromisoformat("2016-09-02")
    assert transactions[0].transaction_code == "IEXX"
    assert transactions[0].transaction_description == "Initial Exam Team nn"
    assert transactions[3].recorded_date == datetime.date.fromisoformat("2016-12-01")
    assert transactions[3].transaction_code == "SMAL"
    assert (
        transactions[3].transaction_description
        == "Applicant Has Filed a Verified Statement of Small Entity Status in Compliance with 37 CFR 1.27"
    )
    assert transactions[-1].recorded_date == datetime.date.fromisoformat("2020-10-21")
    assert transactions[-1].transaction_code == "IDSC"
    assert transactions[-1].transaction_description == "Information Disclosure Statement considered"


def test_patent_term_adjustment(fixture_dir):
    data = json.loads((fixture_dir / "adjustment.json").read_text())
    patent_term_adjustment_data = data["patentBag"][0]["patentTermAdjustmentData"]
    patent_term_adjustment = TermAdjustment(**patent_term_adjustment_data)

    assert patent_term_adjustment.applicant_day_delay_quantity == 15
    assert patent_term_adjustment.overlapping_day_quantity == 0
    assert patent_term_adjustment.filing_date == datetime.date.fromisoformat("2018-09-06")
    assert patent_term_adjustment.c_delay_quantity == 0
    assert patent_term_adjustment.adjustment_total_quantity == 0
    assert patent_term_adjustment.b_delay_quantity == 0
    assert patent_term_adjustment.grant_date == datetime.date.fromisoformat("2021-01-26")
    assert patent_term_adjustment.a_delay_quantity == 142
    assert patent_term_adjustment.non_overlapping_day_quantity == 127
    assert patent_term_adjustment.ip_office_day_delay_quantity == 142

    assert len(patent_term_adjustment.history) > 0
    for history_item in patent_term_adjustment.history:
        assert isinstance(history_item, TermAdjustmentHistory)
        assert history_item.applicant_day_delay_quantity >= 0
        assert isinstance(history_item.start_sequence_number, float)
        assert history_item.case_action_description_text is not None
        assert isinstance(history_item.case_action_sequence_number, float)
        assert history_item.action_date is not None


def test_application_biblio(fixture_dir):
    data = json.loads((fixture_dir / "biblio.json").read_text())
    application_biblio_data = data["patentBag"][0]
    application_biblio = USApplicationBiblio(**application_biblio_data)

    assert application_biblio.aia_indicator is True
    assert application_biblio.app_filing_date == datetime.date.fromisoformat("2016-09-02")
    assert len(application_biblio.inventors) > 0
    assert application_biblio.customer_number == 26161
    assert application_biblio.group_art_unit == "3775"
    assert application_biblio.invention_title == "TONGUE RETRACTORS FOR FRENOTOMIES"
    assert len(application_biblio.correspondence_address) > 0
    assert application_biblio.app_conf_num == 7229
    assert application_biblio.atty_docket_num == "29539-0122US1"
    assert application_biblio.appl_id == "15123456"
    assert application_biblio.first_inventor_name == "Marvin Wang"
    assert application_biblio.first_applicant_name == "The General Hospital Corporation"
    assert len(application_biblio.cpc_classifications) > 0
    assert application_biblio.entity_status == "Small"
    assert application_biblio.status == "Abandoned  --  Failure to Respond to an Office Action"
    assert application_biblio.status_date == datetime.date.fromisoformat("2018-10-02")
    assert application_biblio.status_code is None
    assert application_biblio.patent_number is None


def test_application_object(fixture_dir):
    data = json.loads((fixture_dir / "application.json").read_text())
    application_data = data["patentBag"][0]
    application = USApplication(**application_data)

    assert application.aia_indicator is True
    assert application.app_filing_date == datetime.date.fromisoformat("2016-09-02")
    assert len(application.inventors) > 0
    assert application.customer_number == 26161
    assert application.group_art_unit == "3775"
    assert application.invention_title == "TONGUE RETRACTORS FOR FRENOTOMIES"
    assert len(application.correspondence_address) > 0
    assert application.app_conf_num == 7229
    assert application.atty_docket_num == "29539-0122US1"
    assert application.appl_id == "15123456"
    assert application.first_inventor_name == "Marvin Wang"
    assert application.first_applicant_name == "The General Hospital Corporation"
    assert len(application.cpc_classifications) > 0
    assert application.entity_status == "Small"
    assert application.app_type_code == "UTL"
    assert application.national_stage_indicator is False
    assert application.effective_filing_date == datetime.date.fromisoformat("2016-09-02")
    assert len(application.assignments) > 0
    assert len(application.attorneys.attorneys) > 0
    assert len(application.transactions) > 0
    assert len(application.parent_applications) > 0
    assert len(application.child_applications) > 0
    assert application.status == "Abandoned  --  Failure to Respond to an Office Action"
    assert application.status_date == datetime.date.fromisoformat("2018-10-02")
    assert application.status_code == 161
    assert application.patent_number is None


def test_search_model():
    model = SearchRequest(rangeFilters=[{"field": "filingDate"}])
    assert model.rangeFilters[0].field == "filingDate"
    assert model.rangeFilters[0].valueFrom == "1776-07-04"
    assert model.rangeFilters[0].valueTo == datetime.date.today().isoformat()
