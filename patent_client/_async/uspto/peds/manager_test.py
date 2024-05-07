import datetime
import json
from collections import OrderedDict
from pathlib import Path

import pytest

from .model import PedsPage, USApplication

fixtures = Path(__file__).parent / "fixtures"


class TestPatentExaminationDataDeserialization:
    def test_application(self):
        input_file = fixtures / "app_1_input.json"
        output_file = fixtures / "app_1_output.json"
        app = PedsPage.model_validate_json(input_file.read_text())
        # output_file.write_text(app.model_dump_json(indent=2))
        expected_data = json.loads(output_file.read_text())
        assert json.loads(app.model_dump_json()) == expected_data


class TestPatentExaminationData:
    @pytest.mark.asyncio
    async def test_get_inventors(self):
        app = await USApplication.objects.get(12721698)
        inventors = app.inventors
        assert len(inventors) == 1
        inventor = inventors[0]
        assert inventor.name == "Thind; Deepinder Singh"
        assert inventor.address == "Mankato, MN (US)"

    @pytest.mark.asyncio
    async def test_search_by_customer_number(self):
        result = USApplication.objects.filter(app_cust_number="70155")
        assert await result.count() > 1

    @pytest.mark.asyncio
    async def test_get_by_pub_number(self):
        pub_no = "US20060127129A1"
        app = await USApplication.objects.get(app_early_pub_number=pub_no)
        assert app.patent_title == "ELECTROPHOTOGRAPHIC IMAGE FORMING APPARATUS"

    @pytest.mark.asyncio
    async def test_get_by_pat_number(self):
        pat_no = 6095661
        app = await USApplication.objects.get(patent_number=pat_no)
        assert app.patent_title == "METHOD AND APPARATUS FOR AN L.E.D. FLASHLIGHT"

    @pytest.mark.asyncio
    async def test_get_by_application_number(self):
        app_no = "15145443"
        app = await USApplication.objects.get(app_no)
        assert (
            app.patent_title == "Suction and Discharge Lines for a Dual Hydraulic Fracturing Unit"
        )

    @pytest.mark.asyncio
    async def test_get_many_by_application_number(self):
        app_nos = ["14971450", "15332765", "13441334", "15332709", "14542000"]
        data = USApplication.objects.filter(*app_nos)
        assert await data.count() == 5

    @pytest.mark.asyncio
    async def test_search_pat_by_assignee(self):
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
        apps = [a async for a in data]
        app_titles = [a.patent_title.upper() for a in apps]
        for t in expected_titles:
            assert t in app_titles

    @pytest.mark.asyncio
    async def test_get_many_by_publication_number(self):
        nos = [
            "US20080034424A1",
            "US20100020700A1",
            "US20110225644A1",
            "US20050120054A1",
            "US20050188423A1",
        ]
        data = USApplication.objects.filter(app_early_pub_number=nos)
        assert await data.count() == 5

    @pytest.mark.asyncio
    async def test_get_child_data(self):
        parent = await USApplication.objects.get("16123456")
        child = parent.child_continuity[0]
        assert child.child_appl_id == "17130468"
        assert child.relationship == "claims the benefit of"
        # assert child.child.patent_title == "LEAPFROG TREE-JOIN"

    @pytest.mark.asyncio
    async def test_get_parent_data(self):
        child = await USApplication.objects.get("17130468")
        parent = child.parent_continuity[0]
        assert parent.parent_appl_id == "16123456"
        assert parent.relationship == "is a Division of"
        assert parent.parent_app_filing_date is not None
        # assert parent.parent.patent_title == "Leapfrog Tree-Join"

    @pytest.mark.asyncio
    async def test_pta_history(self):
        app = await USApplication.objects.get("14095073")
        pta_history = app.pta_pte_tran_history
        assert len(pta_history) > 10

    @pytest.mark.asyncio
    async def test_pta_summary(self):
        app = await USApplication.objects.get("14095073")
        expected = OrderedDict(
            [
                ("kind", "PTA"),
                ("a_delay", 169),
                ("pto_delay", 169),
                ("applicant_delay", 10),
                ("total_days", 159),
            ]
        )
        actual = app.pta_pte_summary.model_dump()
        for k, v in expected.items():
            assert actual[k] == v

    @pytest.mark.asyncio
    async def test_transactions(self):
        app = await USApplication.objects.get("14095073")
        assert len(app.transactions) > 70

    @pytest.mark.asyncio
    async def test_correspondent(self):
        app = await USApplication.objects.get("14095073")
        expected_keys = [
            "corr_name",
            "corr_cust_no",
            "corr_address",
        ]

        for k in expected_keys:
            assert getattr(app, k, None) is not None

    @pytest.mark.asyncio
    async def test_attorneys(self):
        app = await USApplication.objects.get("14095073")
        assert len(app.attorneys) > 1
        actual = app.attorneys[0].model_dump()
        assert int(actual["registration_no"]) > 1000
        expected_keys = [
            "registration_no",
            "full_name",
            "phone_num",
            "reg_status",
        ]
        for k in expected_keys:
            assert k in actual

    @pytest.mark.asyncio
    async def test_iterator(self):
        apps = USApplication.objects.filter(first_named_applicant="Tesla").limit(68)
        counter = 0
        try:
            async for a in apps:
                counter += 1
        except KeyError as e:
            raise e
        assert await apps.count() == counter

    @pytest.mark.asyncio
    async def test_expiration_date(self):
        app = await USApplication.objects.get("15384723")
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

        app = await USApplication.objects.get("14865625")
        expected = {
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

    @pytest.mark.asyncio
    @pytest.mark.skip("Expiration date is not supported for PCT applications")
    async def test_expiration_date_for_pct_apps(self):
        app = await USApplication.objects.get("PCT/US2014/020588")
        with pytest.raises(Exception) as exc:
            _ = app.expiration
        assert exc.match("Expiration date not supported for PCT Applications")

    @pytest.mark.asyncio
    async def test_foreign_priority(self):
        app = await USApplication.objects.get(patent_number=10544653)
        fp = app.foreign_priority
        assert isinstance(fp, list)
        app = fp[0]
        assert app.country_name == "NORWAY"
        assert app.filing_date == datetime.date(2017, 2, 15)
        assert app.priority_claim == "20170229"


class TestDocuments:
    @pytest.mark.vcr
    async def test_can_get_document_listing(self):
        app = await USApplication.objects.get(patent_number=10000000)
        docs = app.documents
        assert await docs.count() > 50

    @pytest.mark.vcr
    async def test_can_get_application_from_document(self):
        app = await USApplication.objects.get(patent_number=10000000)
        docs = app.documents
        doc = await docs[5]
        backref_app = await doc.application
        assert app.appl_id == backref_app.appl_id
