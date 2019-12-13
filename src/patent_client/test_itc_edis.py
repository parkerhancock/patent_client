import datetime

from patent_client import ITCInvestigation

import pytest

@pytest.mark.skip("Authentication Problem")
class TestItcEdis:
    def test_can_get_investigation(self):
        inv = ITCInvestigation.objects.get("337-TA-1025")
        assert inv.data == {
            "phase": "Violation",
            "number": "337-1025",
            "status": "Active",
            "title": "Certain Silicon-on-Insulator Wafers; Inv. No. 337-TA-1025",
            "type": "Sec 337",
            "doc_list_url": "https://edis.usitc.gov/data/document?investigationNumber=337-1025&investigationPhase=Violation",
            "docket_number": "3153",
        }

    def test_can_get_documents(self):
        inv = ITCInvestigation.objects.get("337-TA-966")
        print(inv.documents.first().data)
        assert inv.documents.first().data == {
            "investigation_number": "337-966",
            "type": "Voting Sheet",
            "title": None,
            "security": "Public",
            "filing_org": "USITC",
            "filed_by": "Lisa R. Barton",
            "filed_on_behalf_of": "Office of the Secretary",
            "action_jacket_control_number": "GC-16-249",
            "memorandum_control_number": None,
            "attachment_url": "https://edis.usitc.gov/data/attachment/600197",
            "date": datetime.date(2016, 12, 2),
            "last_modified": "2017/05/23 15:43:34",
            "id": "600197",
        }
        assert inv.documents.first().investigation.number == "337-966"

    def test_can_get_attachments(self, tmpdir):
        inv = ITCInvestigation.objects.get("337-TA-1025")
        doc_iterator = iter(inv.documents)
        docs = [next(doc_iterator) for i in range(16)]
        assert docs[15].attachments.first().data == {
            "id": "1163223",
            "document_id": "605365",
            "title": "605365",
            "size": "70956",
            "file_name": "/var/edis/data/sibyl/605365/605365.pdf",
            "pages": "3",
            "created_date": datetime.date(2017, 3, 13),
            "last_modified_date": datetime.date(2017, 3, 13),
            "download_url": "https://edis.usitc.gov/data/download/605365/1163223",
        }
        docs[15].attachments.first().download(tmpdir)
        expected_doc = (
            tmpdir
            / "Granting Respondent's Unopposed Motion for Leave to Designate a Substitute Expert - 605365.pdf"
        )
        exists = expected_doc.exists()
        assert exists
