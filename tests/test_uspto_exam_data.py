import datetime
from collections import OrderedDict

from patent_client import USApplication


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
        data = USApplication.objects.get_many(*app_nos)
        data_list = list(data)
        assert len(data_list) == 5
        assert (
            data_list[4].patent_title
            == "MOBILE, MODULAR, ELECTRICALLY POWERED SYSTEM FOR USE IN FRACTURING UNDERGROUND FORMATIONS"
        )

        assert list(data.values_list("patent_title", flat=True)) == [
            "SYSTEM AND METHOD FOR DEDICATED ELECTRIC SOURCE FOR USE IN FRACTURING UNDERGROUND FORMATIONS USING LIQUID PETROLEUM GAS",
            "ELECTRIC BLENDER SYSTEM, APPARATUS AND METHOD FOR USE IN FRACTURING UNDERGROUND FORMATIONS USING LIQUID PETROLEUM GAS",
            "MOBILE ELECTRIC POWER GENERATION FOR HYDRAULIC FRACTURING OF SUBSURFACE GEOLOGICAL FORMATIONS",
            "MOBILE, MODULAR, ELECTRICALLY POWERED SYSTEM  FOR USE IN FRACTURING UNDERGROUND FORMATIONS",
            "MOBILE, MODULAR, ELECTRICALLY POWERED SYSTEM FOR USE IN FRACTURING UNDERGROUND FORMATIONS",
        ]
        assert list(data.values("appl_id", "app_filing_date")) == [
            OrderedDict(
                [
                    ("appl_id", "15332709"),
                    ("app_filing_date", datetime.date(2016, 10, 24)),
                ]
            ),
            OrderedDict(
                [
                    ("appl_id", "15332765"),
                    ("app_filing_date", datetime.date(2016, 10, 24)),
                ]
            ),
            OrderedDict(
                [
                    ("appl_id", "14971450"),
                    ("app_filing_date", datetime.date(2015, 12, 16)),
                ]
            ),
            OrderedDict(
                [
                    ("appl_id", "13441334"),
                    ("app_filing_date", datetime.date(2012, 4, 6)),
                ]
            ),
            OrderedDict(
                [
                    ("appl_id", "14542000"),
                    ("app_filing_date", datetime.date(2014, 11, 14)),
                ]
            ),
        ]

    def test_values_many_by_application(self):
        app_nos = ["14971450", "15332765", "13441334", "15332709", "14542000"]
        data = USApplication.objects.filter(*app_nos)
        print(list(data.values("inventors__0__nameLineOne")))
        assert list(data.values("inventors__0__nameLineOne")) == [
            OrderedDict([("inventors_0_nameLineOne", "Coli")]),
            OrderedDict([("inventors_0_nameLineOne", "Schelske")]),
            OrderedDict([("inventors_0_nameLineOne", "Morris")]),
            OrderedDict([("inventors_0_nameLineOne", "Coli")]),
            OrderedDict([("inventors_0_nameLineOne", "Coli")]),
        ]

    def test_search_patex_by_assignee(self):
        data = USApplication.objects.filter(first_named_applicant="LogicBlox")
        assert data.order_by("appl_id").values_list("patent_title", flat=True)[:5] == [
            "MAINTENANCE OF ACTIVE DATABASE QUERIES",
            "LEAPFROG TREE-JOIN",
            "SALIENT SAMPLING FOR QUERY SIZE ESTIMATION",
            "TRANSACTION REPAIR",
            "LEAPFROG TREE-JOIN",
        ]

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
        data = USApplication.objects.get_many(
            app_early_pub_number=pubs, patent_number=pats, appl_id=apps
        )
        assert len(data) == 9

    def test_get_search_fields(self):
        result = USApplication.objects.fields
        assert "patent_number" in result
        assert "appl_id" in result
        assert "app_early_pub_number" in result
    
    def test_get_child_data(self):
        parent = USApplication.objects.get('14018930')
        child = parent.children[0]
        assert child.appl_id == '14919159'
        assert child.filing_date == datetime.date(2015, 10, 21)
        assert child.aia == False
        assert child.patent_number == '10120906'
        assert child.status == 'Patented'
        assert child.relationship == 'claims the benefit of'
        assert child.application.patent_title == 'LEAPFROG TREE-JOIN'
        assert child.dict() == {
            'aia': False,
            'appl_id': '14919159',
            'filing_date': datetime.date(2015, 10, 21),
            'patent_number': '10120906',
            'relationship': 'claims the benefit of',
            'status': 'Patented'
        }
    
    def test_get_parent_data(self):
        child = USApplication.objects.get('14018930')
        parent = child.parents[0]
        assert parent.appl_id == '61706484'
        assert parent.filing_date == datetime.date(2012,9,27)
        assert parent.aia == False
        assert parent.patent_number == None
        assert parent.status == 'Expired'
        assert parent.relationship == 'Claims Priority from Provisional Application'
        assert parent.application.patent_title == 'Leapfrog Tree-Join'
        assert parent.dict() == {
            'aia': False,
            'appl_id': '61706484',
            'filing_date': datetime.date(2012,9,27),
            'patent_number': None,
            'relationship': 'Claims Priority from Provisional Application',
            'status': 'Expired'
        }

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
        assert app.pta_pte_summary.dict() == {
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
        assert app.transaction_history[0].dict() == {
            'code': 'C602',
            'date': datetime.date(2013, 12, 3),
            'description': 'Oath or Declaration Filed (Including Supplemental)'
        }

    def test_correspondent(self):
        app = USApplication.objects.get('14095073')
        assert app.correspondent.dict() == {
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
        print(app.attorneys[0].dict())
        assert app.attorneys[0].dict() == {'registration_no': '32429', 'full_name': 'Mims, Peter  ', 'phone_num': '713-758-2732', 'reg_status': 'ACTIVE'}
        
