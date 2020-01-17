import pytest
import datetime
from collections import OrderedDict

from .model import USApplication
import logging

logger = logging.getLogger(__name__)


class TestPatentExaminationData:
    def test_get_inventors(self):
        inventors = USApplication.objects.get(12721698).inventors
        assert len(inventors) == 1
        inventor = inventors[0]
        assert inventor.name == 'Thind; Deepinder Singh'
        assert inventor.city == 'Mankato, '
        assert inventor.geo_code == 'MN'

    def test_search_by_customer_number(self):
        result = USApplication.objects.filter(app_cust_number="70155")
        assert len(result) > 1

    def test_get_by_pub_number(self):
        pub_no = "US20060127129A1"
        app = USApplication.objects.get(app_early_pub_number=pub_no)
        assert app.patent_title == "ELECTROPHOTOGRAPHIC IMAGE FORMING APPARATUS"

    def test_get_by_pat_number(self):
        pat_no = 6095661
        app = USApplication.objects.get(patent_number=pat_no)
        assert app.patent_title == "METHOD AND APPARATUS FOR AN L.E.D. FLASHLIGHT"

    def test_get_by_application_number(self):
        app_no = "15145443"
        app = USApplication.objects.get(app_no)
        assert (
            app.patent_title
            == "Suction and Discharge Lines for a Dual Hydraulic Fracturing Unit"
        )

    def test_get_many_by_application_number(self):
        app_nos = ["14971450", "15332765", "13441334", "15332709", "14542000"]
        data = USApplication.objects.filter(*app_nos)
        assert len(data) == 5

    def test_search_patex_by_assignee(self):
        data = (
            USApplication.objects.filter(first_named_applicant="LogicBlox")
            .order_by("appl_id")
            .limit(4)
        )
        expected_titles = [
            "MAINTENANCE OF ACTIVE DATABASE QUERIES",
            "SALIENT SAMPLING FOR QUERY SIZE ESTIMATION",
            "TRANSACTION REPAIR",
            "LEAPFROG TREE-JOIN",
        ]
        app_titles = data.values_list("patent_title", flat=True)
        app_titles = [a.upper() for a in app_titles]
        for t in expected_titles:
            assert t in app_titles

    def test_get_many_by_publication_number(self):
        nos = [
            "US20080034424A1",
            "US20100020700A1",
            "US20110225644A1",
            "US20050120054A1",
            "US20050188423A1",
        ]
        data = USApplication.objects.filter(app_early_pub_number=nos)
        assert len(list(data)) == 5

    def test_mixed_get_many(self):
        pats = ["7627658", "7551922", "7359935"]
        pubs = ["US20080034424A1", "US20100020700A1", "US20110225644A1"]
        apps = ["14971450", "15332765", "13441334"]
        data = USApplication.objects.filter(
            app_early_pub_number=pubs, patent_number=pats, appl_id=apps
        )
        assert len(data) == 9

    def test_get_search_fields(self):
        result = USApplication.objects.allowed_filters
        assert "patent_number" in result
        assert "appl_id" in result
        assert "app_early_pub_number" in result

    def test_get_child_data(self):
        parent = USApplication.objects.get("14018930")
        child = parent.child_continuity[0]
        assert child.child_appl_id == "14919159"
        assert child.relationship == "claims the benefit of"
        #assert child.child.patent_title == "LEAPFROG TREE-JOIN"

    def test_get_parent_data(self):
        child = USApplication.objects.get("14018930")
        parent = child.parent_continuity[0]
        assert parent.parent_appl_id == "61706484"
        assert parent.relationship == "Claims Priority from Provisional Application"
        assert parent.parent_app_filing_date is not None
        #assert parent.parent.patent_title == "Leapfrog Tree-Join"

    def test_pta_history(self):
        app = USApplication.objects.get("14095073")
        pta_history = app.pta_pte_tran_history
        assert len(pta_history) > 10

    def test_pta_summary(self):
        app = USApplication.objects.get("14095073")
        expected = OrderedDict(
            [
                ("kind", "PTA"),
                ("a_delay", 169),
                ("pto_delay", 169),
                ("applicant_delay", 10),
                ("total_days", 159),
            ]
        )
        actual = app.pta_pte_summary.as_dict()
        for k, v in expected.items():
            assert actual[k] == v

    def test_transactions(self):
        app = USApplication.objects.get("14095073")
        assert len(app.transactions) > 70

    def test_correspondent(self):
        app = USApplication.objects.get("14095073")
        correspondent = app.correspondent.as_dict()
        expected = {
            "name": "VINSON & ELKINS L.L.P.",
            "cust_no": "22892",
            "street": "1001 Fannin Street\nSuite 2500",
            "city": "HOUSTON",
            "geo_region_code": "TX",
            "postal_code": "77002-6760",
        }
        for k in expected.keys():
            assert expected[k] == correspondent[k]

    def test_attorneys(self):
        app = USApplication.objects.get("14095073")
        assert len(app.attorneys) > 1
        actual = app.attorneys[0].as_dict() 
        expected = {
            "registration_no": "32429",
            "full_name": "Mims, Peter  ",
            "phone_num": "713-758-2732",
            "reg_status": "ACTIVE",
        }
        for k in expected.keys():
            assert expected[k] == actual[k]

    def test_iterator(self):
        apps = USApplication.objects.filter(first_named_applicant="Tesla").limit(68)
        counter = 0
        try:
            for a in apps:
                counter += 1
        except KeyError as e:
            raise e
        assert len(apps) == counter

    def test_expiration_date(self):
        app = USApplication.objects.get("15384723")
        expected = {
            "parent_appl_id": "12322218",
            "parent_app_filing_date": datetime.date(2009, 1, 29),
            "parent_relationship": "is a Continuation in part of",
            "initial_term": datetime.date(2029, 1, 29),
            "pta_or_pte": 0,
            "extended_term": datetime.date(2029, 1, 29),
            "terminal_disclaimer_filed": True,
        }
        actual = dict(app.expiration)
        for k in expected.keys():
            assert expected[k] == actual[k]

        app = USApplication.objects.get("14865625")
        expected =  {
            "parent_appl_id": "14865625",
            "parent_app_filing_date": datetime.date(2015, 9, 25),
            "parent_relationship": "self",
            "initial_term": datetime.date(2035, 9, 25),
            "pta_or_pte": 752,
            "extended_term": datetime.date(2037, 10, 16),
            "terminal_disclaimer_filed": False,
        }
        actual = dict(app.expiration)
        for k in expected.keys():
            assert expected[k] == actual[k]

    def test_expiration_date_for_pct_apps(self):
        app = USApplication.objects.get("PCT/CA02/01413")
        with pytest.raises(Exception) as exc:
            expiration_data = app.expiration
        assert exc.match("Expiration date not supported for PCT Applications")

    def test_issue_25(self):
        company_name = "Tesla"
        records = list(
            USApplication.objects.filter(first_named_applicant=company_name)
            .limit(5)
            .values("app_filing_date", "patent_number", "patent_title")[:]
        )
        assert len(records) >= 4

    def test_get_applicant(self):
        applicants = USApplication.objects.filter(first_named_applicant="Tesla").first().applicants
        assert applicants[0].name == 'Tesla Laboratories, LLC'
    

