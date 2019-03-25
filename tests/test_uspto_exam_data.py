import datetime
from collections import OrderedDict

from patent_client import USApplication
from patent_client.util import Manager
Manager.test_mode = True

class TestPatentExaminationData:
    
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
        data_list = list(data)
        assert len(data_list) == 5

    def test_search_patex_by_assignee(self):
        data = USApplication.objects.filter(first_named_applicant="LogicBlox")
        expected_titles = [
            "MAINTENANCE OF ACTIVE DATABASE QUERIES",
            "SALIENT SAMPLING FOR QUERY SIZE ESTIMATION",
            "TRANSACTION REPAIR",
            "LEAPFROG TREE-JOIN",
        ]
        app_titles = data.order_by("appl_id").values_list("patent_title", flat=True)
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
        parent = USApplication.objects.get('14018930')
        child = parent.children[0]
        assert child.child_appl_id == '14919159'
        assert child.relationship == 'claims the benefit of'
        assert child.child.patent_title == 'LEAPFROG TREE-JOIN'
    
    def test_get_parent_data(self):
        child = USApplication.objects.get('14018930')
        parent = child.parents[0]
        assert parent.parent_appl_id == '61706484'
        assert parent.relationship == 'Claims Priority from Provisional Application'
        assert parent.parent.patent_title == 'Leapfrog Tree-Join'
    def test_pta_history(self):
        app = USApplication.objects.get('14095073')
        pta_history = app.pta_pte_history
        assert len(pta_history) > 10
        entry = pta_history[0]
        assert entry.number == 0.5
        assert entry.date == datetime.date(2013,12,3)
        assert entry.description == 'Filing date'
        assert entry.pto_days == 0
        assert entry.applicant_days == 0
        assert entry.start == 0.0

    def test_pta_summary(self):
        app = USApplication.objects.get('14095073')
        assert app.pta_pte_summary.as_dict() == {
            'type': 'PTA', 
            'a_delay': 169, 
            'b_delay': 0, 
            'c_delay': 0, 
            'overlap_delay': 0, 
            'pto_delay': 169, 
            'applicant_delay': 10, 
            'pto_adjustments': 0, 
            'total_days': 159}

    def test_transactions(self):
        app = USApplication.objects.get('14095073')
        assert len(app.transaction_history) > 70
        assert app.transaction_history[0].as_dict() == {
            'code': 'C602',
            'date': datetime.date(2013, 12, 3),
            'description': 'Oath or Declaration Filed (Including Supplemental)'
        }

    def test_correspondent(self):
        app = USApplication.objects.get('14095073')
        print(app.correspondent.as_dict())
        assert app.correspondent.as_dict() == {
            'name_line_one': 'VINSON & ELKINS L.L.P.', 
            'cust_no': '22892', 
            'street_line_one': 'First City Tower, 1001 Fannin Street', 
            'street_line_two': 'Suite 2500', 
            'city': 'HOUSTON', 
            'geo_region_code': 'TX', 
            'postal_code': '77002-6760'
        }

    def test_attorneys(self):
        app = USApplication.objects.get('14095073')
        assert len(app.attorneys) > 1
        print(app.attorneys[0].as_dict())
        assert app.attorneys[0].as_dict() == {'registration_no': '32429', 'full_name': 'Mims, Peter  ', 'phone_num': '713-758-2732', 'reg_status': 'ACTIVE'}
        
    def test_iterator(self):
        apps = USApplication.objects.filter(first_named_applicant='Tesla')
        counter = 0
        try:
            for a in apps:
                counter += 1
        except KeyError as e:
            print(counter)
            print(len(apps))
            raise e
        assert len(apps) == counter
    
    def test_expiration_date(self):
        app = USApplication.objects.get('15384723')
        assert app.expiration == {
            'parent_appl_id': '12322218', 
            'parent_app_filing_date': datetime.date(2009, 1, 29), 
            'parent_relationship': 'is a Continuation in part of', 
            '20_year_term': datetime.date(2029, 1, 29), 
            'pta_or_pte': 0, 
            'extended_term': datetime.date(2029, 1, 29), 
            'terminal_disclaimer_filed': True
            }
        app = USApplication.objects.get('14865625')
        assert app.expiration == {
            'parent_appl_id': '14865625', 
            'parent_app_filing_date': datetime.date(2015, 9, 25), 
            'parent_relationship': 'self', 
            '20_year_term': datetime.date(2035, 9, 25), 
            'pta_or_pte': 752, 
            'extended_term': datetime.date(2037, 10, 16), 
            'terminal_disclaimer_filed': False
            }
    
    def test_issue_25(self):
        company_name = 'Tesla'
        records = list(USApplication.objects
                .filter(first_named_applicant=company_name)
                .values('app_filing_date', 'patent_number', 'patent_title')[:]
            )
        assert len(records) >= 400
    
