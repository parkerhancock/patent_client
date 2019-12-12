import os
from tempfile import TemporaryDirectory
import datetime
import pytest
from . import Assignment


class TestAssignment:
    def test_fetch_assignments_by_assignee(self):
        assignments = Assignment.objects.filter(assignee="US Well Services")
        assert len(assignments) >= 22
        assert assignments[5].assignors[0].name == "OEHRING, JARED"
        assignments = Assignment.objects.filter(assignee="LogicBlox")
        assert len(assignments) >= 9

    def test_fetch_assignments_by_patent(self):
        assignments = Assignment.objects.filter(patent_number="8,789,601")
        assert len(assignments) >= 1
        assert "48041-605" in [a.id for a in assignments]

    def test_fetch_assignments_by_application(self):
        assignments = Assignment.objects.filter(appl_id="14/190,982")
        assert len(assignments) >= 1

    def test_fetch_assignee_with_greater_than_500_assignments(self):
        assignments = Assignment.objects.filter(assignee="Borealis")
        assert len(assignments) >= 1268

    def test_get_assignment_image(self):
        assignments = Assignment.objects.filter(patent_number=6095661)
        assignment = assignments[0]
        assert (
            assignment.image_url
            == "http://legacy-assignments.uspto.gov/assignments/assignment-pat-038505-0128.pdf"
        )

    def test_slice_assignments(self):
        assignments = Assignment.objects.filter(assignee="US Well Services")
        assignment_list1 = [assignment.id for assignment in assignments[0:5]]
        assert len(assignment_list1) == 5

        assignment_list2 = [assignment.id for assignment in assignments[:5]]
        assert len(assignment_list2) == 5

        assignment_list3 = [assignment.id for assignment in assignments[-5:]]
        assert len(assignment_list3) == 5

    def test_iterate_assignments(self):
        assignments = Assignment.objects.filter(assignee="US Well Services")
        assignment_list = [assignment.id for assignment in assignments]
        #import pdb; pdb.set_trace()
        assert len(assignment_list) == len(assignments)

    def test_bug_scidrill(self):
        assignments = Assignment.objects.filter(assignee="Scientific Drilling")
        assignment_list = list(assignments.values_list("appl_num", flat=True))
        assert len(assignment_list) == 58


class TestAssignmentBugs:
    def test_id_43433_231(self):
        assignment = Assignment.objects.get("43433-231")
        assert assignment.properties[0].filing_date == datetime.date(2016, 10, 25)
