import json

import pytest
import datetime
from collections import OrderedDict

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

    def test_get_many_by_application_number(self):
        app_nos = ["14971450", "15332765", "13441334", "15332709", "14542000"]
        data = USApplication.objects.get_many(*app_nos)
        data_list = list(data)
        assert len(data_list) == 5
        assert (
            data_list[4].patent_title
            == "MOBILE, MODULAR, ELECTRICALLY POWERED SYSTEM FOR USE IN FRACTURING UNDERGROUND FORMATIONS"
        )
        
        assert list(data.values_list('patent_title', flat=True)) == ['SYSTEM AND METHOD FOR DEDICATED ELECTRIC SOURCE FOR USE IN FRACTURING UNDERGROUND FORMATIONS USING LIQUID PETROLEUM GAS', 'ELECTRIC BLENDER SYSTEM, APPARATUS AND METHOD FOR USE IN FRACTURING UNDERGROUND FORMATIONS USING LIQUID PETROLEUM GAS', 'MOBILE ELECTRIC POWER GENERATION FOR HYDRAULIC FRACTURING OF SUBSURFACE GEOLOGICAL FORMATIONS', 'MOBILE, MODULAR, ELECTRICALLY POWERED SYSTEM  FOR USE IN FRACTURING UNDERGROUND FORMATIONS', 'MOBILE, MODULAR, ELECTRICALLY POWERED SYSTEM FOR USE IN FRACTURING UNDERGROUND FORMATIONS']
        assert list(data.values('appl_id', 'app_filing_date')) == [
            OrderedDict([('appl_id', '15332709'),
             ('app_filing_date', datetime.date(2016, 10, 24))]),
            OrderedDict([('appl_id', '15332765'),
            ('app_filing_date', datetime.date(2016, 10, 24))]),
            OrderedDict([('appl_id', '14971450'),
            ('app_filing_date', datetime.date(2015, 12, 16))]),
            OrderedDict([('appl_id', '13441334'),
            ('app_filing_date', datetime.date(2012, 4, 6))]),
            OrderedDict([('appl_id', '14542000'),
            ('app_filing_date', datetime.date(2014, 11, 14))])]

    def test_values_many_by_application(self):
        app_nos = ["14971450", "15332765", "13441334", "15332709", "14542000"]
        data = USApplication.objects.get_many(*app_nos) 
        print(list(data.values('inventors__0__nameLineOne')))
        assert list(data.values('inventors__0__nameLineOne')) == [OrderedDict([('inventors_0_nameLineOne', 'Todd  Coli')]), OrderedDict([('inventors_0_nameLineOne', 'Schelske, Eldon')]), OrderedDict([('inventors_0_nameLineOne', 'Jeffrey G. Morris')]), OrderedDict([('inventors_0_nameLineOne', 'Todd  Coli')]), OrderedDict([('inventors_0_nameLineOne', 'Todd  Coli')])]

    def test_search_patex_by_assignee(self):
        data = USApplication.objects.filter(first_named_applicant="Scientific Drilling, Inc.")
        assert data.order_by('appl_id').values_list('patent_title', flat=True)[:5] == ['DOWNHOLE APPARATUS FOR ELECTRICAL POWER GENERATION FROM SHAFT FLEXURE',
 'Hybrid Bearings for Downhole Motors',
 'DOUBLE SHAFT DRILLING APPARATUS WITH HANGER BEARINGS',
 'DRILL BIT FOR A DRILLING APPARATUS',
 "METHOD TO DETERMINE LOCAL VARIATIONS OF THE EARTH'S MAGNETIC FIELD AND "
 'LOCATION OF THE SOURCE THEREOF']

    def test_get_many_by_publication_number(self):
        nos = [
            "US20080034424A1",
            "US20100020700A1",
            "US20110225644A1",
            "US20050120054A1",
            "US20050188423A1",
        ]
        data = USApplication.objects.get_many(app_early_pub_number=nos)
        assert len(list(data)) == 5

    #@pytest.mark.skip('This function doesn\'nt work with the ORM Style. Consider dropping it')
    def test_mixed_get_many(self):
        pats = ["7627658", "7551922", "7359935"]
        pubs = ["US20080034424A1", "US20100020700A1", "US20110225644A1"]
        apps = ["14971450", "15332765", "13441334"]
        data = USApplication.objects.get_many(
            app_early_pub_number=pubs, patent_number=pats, appl_id=apps
        )
        assert len(data) == 9

    def test_get_search_fields(self):
        result = USApplication.objects.fields()
        assert "patent_number" in result
        assert "appl_id" in result
        assert "app_early_pub_number" in result
