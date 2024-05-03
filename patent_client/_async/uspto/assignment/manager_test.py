import datetime

import pytest

from .model import Assignment


class TestAssignment:
    @pytest.mark.asyncio
    async def test_get_assignment(self):
        a = await Assignment.objects.get("18247-405")
        assert a.id == "18247-405"
        assert a.conveyance_text == "NUNC PRO TUNC ASSIGNMENT"
        assert a.last_update_date <= datetime.date.fromisoformat("2008-01-22")
        assert a.transaction_date.isoformat() == "2019-07-11"
        assert a.recorded_date.isoformat() == "2006-09-14"
        assert a.correspondent.name == "JEFFREY H. INGERMAN"
        assert (
            a.correspondent.address
            == "FISH & NEAVE IP GROUP, ROPES & GRAY LLP\n1251 AVENUE OF THE AMERICAS C3\nNEW YORK, NY 10020-1105"
        )
        assert len(a.assignors) == 1
        assert a.assignors[0].name == "REALTIME DATA COMPRESSION SYSTEMS, INC."
        assert a.assignors[0].execution_date.isoformat() == "2006-09-14"
        assert len(a.assignees) == 1
        assert a.assignees[0].name == "REALTIME DATA LLC"
        assert a.assignees[0].address == "15 WEST 36TH STREET\nNEW YORK, NEW YORK 10018"
        assert len(a.properties) == 5
        assert (
            a.properties[0].invention_title
            == "SYSTEM AND METHODS FOR ACCELERATED DATA STORAGE AND RETRIEVAL"
        )
        assert a.properties[0].appl_num == "10628795"
        assert a.properties[0].filing_date.isoformat() == "2003-07-28"
        assert a.properties[0].intl_publ_date is None
        assert a.properties[0].intl_reg_num is None
        assert a.properties[0].inventors == "James J. Fallon"
        assert a.properties[0].issue_date.isoformat() == "2006-10-31"
        assert a.properties[0].pat_num == "7130913"
        assert a.properties[0].pct_num is None
        assert a.properties[0].publ_date.isoformat() == "2004-04-15"
        assert a.properties[0].publ_num == "20040073746"

    @pytest.mark.asyncio
    async def test_fetch_assignments_by_assignee(self):
        assignments = Assignment.objects.filter(assignee="US Well Services")
        assert await assignments.count() >= 22
        assert (await assignments[5]).assignors[0].name == "OEHRING, JARED"
        assignments = Assignment.objects.filter(assignee="LogicBlox")
        assert await assignments.count() >= 9

    @pytest.mark.asyncio
    async def test_fetch_assignments_by_patent(self):
        assignments = Assignment.objects.filter(patent_number="8,789,601")
        assert await assignments.count() >= 1
        assert "48041-605" in [a.id async for a in assignments]

    @pytest.mark.asyncio
    async def test_fetch_assignments_by_application(self):
        assignments = Assignment.objects.filter(appl_id="14/190,982")
        assert await assignments.count() >= 1

    @pytest.mark.asyncio
    async def test_fetch_assignee_with_greater_than_500_assignments(self):
        assignments = Assignment.objects.filter(assignee="Borealis")
        assert await assignments.count() >= 1268

    @pytest.mark.asyncio
    async def test_get_assignment_image(self):
        assignments = Assignment.objects.filter(patent_number=6095661)
        assignment = await assignments.first()
        assert (
            assignment.image_url
            == "http://legacy-assignments.uspto.gov/assignments/assignment-pat-038505-0128.pdf"
        )

    @pytest.mark.asyncio
    async def test_slice_assignments(self):
        assignments = Assignment.objects.filter(assignee="US Well Services")
        assignment_list1 = [assignment.id async for assignment in await assignments[0:5]]
        assert len(assignment_list1) == 5

        assignment_list2 = [assignment.id async for assignment in await assignments[:5]]
        assert len(assignment_list2) == 5

        assignment_list3 = [assignment.id async for assignment in await assignments[-5:]]
        assert len(assignment_list3) == 5

    @pytest.mark.asyncio
    async def test_iterate_assignments(self):
        assignments = Assignment.objects.filter(assignee="US Well Services")
        assignment_list = [assignment.id async for assignment in assignments]
        assert len(assignment_list) == await assignments.count()
