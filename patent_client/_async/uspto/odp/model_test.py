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
    assert continuity.request_identifier == "b5622b59-380c-4cb0-8525-2e2eadaeaa05"
    assert len(continuity.parent_continuity) == 1
    parent = continuity.parent_continuity[0]
    assert parent.parent_application_id == "PCT/IB2013/001896"
    assert parent.parent_application_status_code == 150
    assert parent.parent_application_status == "Patented Case"
    assert parent.parent_filing_date == datetime.date(2013, 7, 2)
    assert parent.claim_type_code == "NST"
    assert parent.claim_type_description == "is a National Stage Entry of"
    assert parent.child_application_id == "14412875"

    assert len(continuity.child_continuity) == 3
    child = continuity.child_continuity[0]
    assert child.child_application_id == "17013096"
    assert child.child_application_status_code == 150
    assert child.child_application_status == "Patented Case"
    assert child.child_filing_date == datetime.date(2020, 9, 4)
    assert child.claim_type_code == "CON"
    assert child.claim_type_description == "is a Continuation of"
    assert child.parent_application_id == "14412875"
    assert child.child_patent_number == "11612758"
    assert child.child_aia_indicator is False


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
            assert isinstance(download_option.get("pageTotalQuantity"), (int, type(None)))


def test_assignment(fixture_dir):
    data = json.loads((fixture_dir / "assignment.json").read_text())
    assignment_bag = data["patentFileWrapperDataBag"][0]["assignmentBag"]
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
    foreign_priority_bag = data["patentFileWrapperDataBag"][0]["foreignPriorityBag"]
    for foreign_priority_data in foreign_priority_bag:
        foreign_priority = ForeignPriority(**foreign_priority_data)
        assert foreign_priority.priority_number_text is not None
        assert isinstance(foreign_priority.filing_date, datetime.date)
        assert foreign_priority.ip_office is not None


def test_attorney(fixture_dir):
    data = json.loads((fixture_dir / "attorney.json").read_text())
    customer_number = CustomerNumber(**data["patentFileWrapperDataBag"][0]["recordAttorney"])
    assert customer_number.customer_number == 25005
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
            assert telecom.telecom_type_code in ["FAX", "TEL", "EMAIL"]
    assert customer_number.address is not None
    assert customer_number.address.city_name == "Brookfield"
    assert customer_number.address.geographic_region_code == "WI"
    assert customer_number.address.country_code == "US"
    assert customer_number.address.postal_code == "53005"
    assert customer_number.address.country_name == "UNITED STATES"
    assert customer_number.address.address_line_one_text == "13845 Bishops Drive"


def test_transactions(fixture_dir):
    data = json.loads((fixture_dir / "transactions.json").read_text())
    transactions = [
        Transaction(**transaction_data)
        for transaction_data in data["patentFileWrapperDataBag"][0]["eventDataBag"]
    ]
    for transaction in transactions:
        assert transaction.event_date is not None
        assert transaction.event_code is not None
        assert transaction.event_description is not None
        # Test for specific transaction details based on the provided fixtures
    assert transactions[0].event_date == datetime.date.fromisoformat("2023-12-04")
    assert transactions[0].event_code == "M1551"
    assert transactions[0].event_description == "Payment of Maintenance Fee, 4th Year, Large Entity"
    assert transactions[3].event_date == datetime.date.fromisoformat("2020-09-08")
    assert transactions[3].event_code == "PGM/"
    assert transactions[3].event_description == "Recordation of Patent Grant Mailed"
    assert transactions[-1].event_date == datetime.date.fromisoformat("2015-01-05")
    assert transactions[-1].event_code == "IEXX"
    assert transactions[-1].event_description == "Initial Exam Team nn"


def test_patent_term_adjustment(fixture_dir):
    data = json.loads((fixture_dir / "adjustment.json").read_text())
    patent_term_adjustment_data = data["patentFileWrapperDataBag"][0]["patentTermAdjustmentData"]
    patent_term_adjustment = TermAdjustment(**patent_term_adjustment_data)

    assert patent_term_adjustment.applicant_day_delay_quantity == 88
    assert patent_term_adjustment.overlapping_day_quantity == 81
    assert patent_term_adjustment.filing_date == datetime.date.fromisoformat("2019-03-02")
    assert patent_term_adjustment.c_delay_quantity == 0
    assert patent_term_adjustment.adjustment_total_quantity == 1092
    assert patent_term_adjustment.b_delay_quantity == 511
    assert patent_term_adjustment.grant_date == datetime.date.fromisoformat("2023-09-19")
    assert patent_term_adjustment.a_delay_quantity == 750
    assert patent_term_adjustment.ip_office_day_delay_quantity == 1180

    assert len(patent_term_adjustment.history) > 0
    for history_item in patent_term_adjustment.history:
        assert isinstance(history_item, TermAdjustmentHistory)
        assert isinstance(history_item.applicant_days, (int, type(None)))
        assert isinstance(history_item.originating_event_sequence_number, float)
        assert history_item.event_description_text is not None
        assert isinstance(history_item.event_sequence_number, (float, type(None)))
        assert history_item.event_date is not None


def test_application_biblio(fixture_dir):
    data = json.loads((fixture_dir / "biblio.json").read_text())
    application_biblio_data = data["patentFileWrapperDataBag"][0]
    application_biblio = USApplicationBiblio(**application_biblio_data)

    assert application_biblio.aia_indicator is True
    assert application_biblio.app_filing_date == datetime.date.fromisoformat("2019-03-02")
    assert len(application_biblio.inventors) > 0
    assert application_biblio.customer_number == 23595
    assert application_biblio.group_art_unit == "2481"
    assert (
        application_biblio.invention_title
        == "ILLUMINATING SYSTEM FOR DETERMINING THE TOPOGRAPHY OF THE CORNEA OF AN EYE"
    )
    assert application_biblio.app_conf_num == 5169
    assert application_biblio.atty_docket_num == "104628.0009"
    assert application_biblio.appl_id == "16330077"
    assert application_biblio.first_inventor_name == "Beate BÖHME"
    assert application_biblio.first_applicant_name == "Carl Zeiss Meditec AG"
    assert len(application_biblio.cpc_classifications) > 0
    assert application_biblio.entity_status == "Regular Undiscounted"
    assert application_biblio.status == "Patented Case"
    assert application_biblio.status_date == datetime.date.fromisoformat("2023-08-30")
    assert application_biblio.status_code == 150
    assert application_biblio.patent_number == "11759105"
    assert application_biblio.grant_date == datetime.date.fromisoformat("2023-09-19")


def test_application_object(fixture_dir):
    data = json.loads((fixture_dir / "application.json").read_text())
    application_data = data["patentFileWrapperDataBag"][0]
    application = USApplication(**application_data)

    assert application.aia_indicator is False
    assert application.app_filing_date == datetime.date.fromisoformat("2015-01-05")
    assert len(application.inventors) > 0
    assert application.customer_number == 26111
    assert application.group_art_unit == "3791"
    assert (
        application.invention_title
        == "Device For Repetitive Nerve Stimulation In Order To Break Down Fat Tissue Means Of Inductive Magnetic Fields"
    )
    assert len(application.correspondence_address) > 0
    assert application.app_conf_num == 6393
    assert application.atty_docket_num == "4387.0210001"
    assert application.appl_id == "14412875"
    assert application.first_inventor_name == "Tobias Sokolowski"
    assert application.first_applicant_name == "BTL Medical Technologies S.R.O."
    assert len(application.cpc_classifications) > 0
    assert application.entity_status == "Regular Undiscounted"
    assert application.app_type_code == "UTL"
    assert application.national_stage_indicator is False
    assert application.effective_filing_date == datetime.date.fromisoformat("2015-01-05")
    assert len(application.assignments) > 0
    assert len(application.attorneys.attorneys) > 0
    assert len(application.transactions) > 0
    assert len(application.parent_applications) > 0
    assert len(application.child_applications) > 0
    assert application.status == "Patented Case"
    assert application.status_date == datetime.date.fromisoformat("2020-08-19")
    assert application.status_code == 150
    assert application.patent_number == "10765880"


def test_search_model():
    model = SearchRequest(rangeFilters=[{"field": "filingDate"}])
    assert model.rangeFilters[0].field == "filingDate"
    assert model.rangeFilters[0].valueFrom == "1776-07-04"
    assert model.rangeFilters[0].valueTo == datetime.date.today().isoformat()
