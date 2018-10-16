import json

import pytest
import datetime

from ip.uspto_exam_data import USApplication

class TestPatentExaminationData:
    """
    def test_search_by_customer_number(self):
        result = USApplication.objects.search(app_cust_number="70155")
        print(json.dumps(result))
        assert False
    """

    def test_get_by_pub_number(self):
        pub_no = "US20060127129A1"
        app = USApplication.objects.get(app_early_pub_number=pub_no)
        assert app.patent_title == "ELECTROPHOTOGRAPHIC IMAGE FORMING APPARATUS"

    def test_get_by_pat_number(self):
        pat_no = 6095661
        app = USApplication.objects.get(patent_number=pat_no)
        assert (
            app.patent_title == "METHOD AND APPARATUS FOR AN L.E.D. FLASHLIGHT"
        )

    def test_get_by_application_number(self):
        app_no = "15145443"
        app = USApplication.objects.get(app_no)
        assert (
            app.patent_title
            == "Suction and Discharge Lines for a Dual Hydraulic Fracturing Unit"
        )

    def test_bulk_get_by_application_number(self):
        app_nos = ["14971450", "15332765", "13441334", "15332709", "14542000"]
        data = USApplication.objects.bulk_get(app_nos)
        assert len(data) == 5
        assert (
            data[4].patent_title
            == "MOBILE, MODULAR, ELECTRICALLY POWERED SYSTEM FOR USE IN FRACTURING UNDERGROUND FORMATIONS"
        )

    @pytest.mark.skip()
    def test_search_patex_by_assignee(self):
        data = USApplication.objects.search(first_named_applicant="Scientific Drilling, Inc.")
        from pprint import pprint

        pprint(data[:5])
        assert data[5].dict == {
            "applicants": [
                {
                    "city": "Houston",
                    "country": "US",
                    "name": "Scientific Drilling International, Inc.",
                    "region": "TX",
                    "region_type": "State",
                }
            ],

                "aia_status": "false",
                "app_attorney_dock_number": "SDI.043002",
                "app_cls_subcls": "702/006000",
                "app_cust_number": "100183",
                "app_early_pub_date": datetime.date(2014, 3, 20),
                "app_early_pub_number": "US20140081574A1",
                "app_examiner": "BHAT, ADITYA S",
                "app_filing_date": datetime.date(2013, 9, 9),
                "app_group_art_unit": "2863",
                "app_id": "14021602",
                "app_status": "Patented Case",
                "app_status_date": datetime.date(2016, 8, 31),
                "app_type": "Utility",
                "entity_status": "UNDISCOUNTED",
                "file_location": "ELECTRONIC",
                "patent_issue_date": datetime.date(2016, 9, 20),
                "patent_number": "9448329",
                "title": "METHOD TO DETERMINE LOCAL VARIATIONS OF THE EARTH'S "
                "MAGNETIC FIELD AND LOCATION OF THE SOURCE THEREOF",

            "inventors": [
                {
                    "city": "Minneapolis",
                    "country": "US",
                    "name": "Jim Hove",
                    "region": "MN",
                    "region_type": "State",
                }
            ],
            "transactions": [],
        }

    def test_bulk_get_by_publication_number(self):
        nos = [
            "US20080034424A1",
            "US20100020700A1",
            "US20110225644A1",
            "US20050120054A1",
            "US20050188423A1",
        ]
        data = USApplication.objects.bulk_get(app_early_pub_number=nos)
        assert len(data) == 5

    @pytest.mark.skip('This function doesn\'nt work with the ORM Style. Consider dropping it')
    def test_mixed_bulk_get(self):
        pats = ["US7627658", "US7551922", "US7359935"]
        pubs = ["20080034424", "20100020700", "20110225644"]
        apps = ["14971450", "15332765", "13441334"]
        data = USApplication.objects.bulk_get(
            app_early_pub_number=pubs, patent_number=pats, appl_id=apps
        )
        assert len(data) == 9

    def test_get_search_fields(self):
        result = USApplication.objects.fields()
        assert "patent_number" in result
        assert "appl_id" in result
        assert "app_early_pub_number" in result
