import datetime

import pytest

from .model import ITCInvestigation


@pytest.mark.skip("EDIS out of scope for now")
class TestItcEdis:
    def test_can_get_investigation(self):
        inv = ITCInvestigation.objects.get("337-TA-1025")
        expected = {
            "phase": "Violation",
            "number": "337-1025",
            "status": "Inactive",
            "title": "Certain Silicon-on-Insulator Wafers; Inv. No. 337-TA-1025",
            "type": "Sec 337",
            "docket_number": "3153",
        }
        for k, v in expected.items():
            assert getattr(inv, k) == v

    def test_can_get_documents(self):
        inv = ITCInvestigation.objects.get("337-TA-966")
        document = inv.documents.first()
        expected = {
            "type": "Voting Sheet",
            "title": None,
            "security": "Public",
            "filing_party": "USITC",
            "filed_by": "Lisa R. Barton",
            "filed_on_behalf_of": "Office of the Secretary",
            "action_jacket_control_number": "GC-16-249",
            "memorandum_control_number": None,
            "date": datetime.date(2016, 12, 2),
            "last_modified": datetime.datetime(2017, 5, 23, 15, 43, 34),
            "id": 600197,
        }
        for k, v in expected.items():
            assert getattr(document, k) == v
        assert inv.documents.first().investigation.number == "337-966"

    @pytest.mark.skip("EDIS Attachment API not working")
    def test_can_get_attachments(self, tmpdir):
        inv = ITCInvestigation.objects.get("337-TA-1025")
        doc_iterator = iter(inv.documents)
        docs = [next(doc_iterator) for i in range(16)]
        attachment = docs[15].attachments.first()
        expected = {
            "id": 1163223,
            "document_id": 605365,
            "title": "605365",
            "file_size": 70956,
            "file_name": "/var/edis/data/sibyl/605365/605365.pdf",
            "pages": 3,
            "created_date": datetime.datetime(2017, 3, 13, 14, 57, 45),
            "last_modified_date": datetime.datetime(2017, 3, 13, 15, 26, 17),
            "download_url": "https://edis.usitc.gov/data/download/605365/1163223",
        }
        for k, v in expected.items():
            assert getattr(attachment, k) == v

        docs[15].attachments.first().download(tmpdir)
        expected_doc = (
            tmpdir / "Granting Respondent's Unopposed Motion for Leave to Designate a Substitute Expert - 605365.pdf"
        )
        exists = expected_doc.exists()
        assert exists
