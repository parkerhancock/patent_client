import pytest
import datetime

from patent_client import Inpadoc, Epo, Assignment, USApplication
from patent_client.util import Manager
Manager.test_mode = True

class TestReadmeExamples():

    def test_us_applications(self):
        app = USApplication.objects.get('15710770')
        assert app.patent_title == 'Camera Assembly with Concave-Shaped Front Face'

    def test_assignments(self):
        assignments = Assignment.objects.filter(assignee='Google')
        assert len(assignments) >= 23860
        assignment = Assignment.objects.get('47086-788')
        assert assignment.conveyance_text == 'ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).'

    def test_inpadoc(self):
        pub = Inpadoc.objects.get('EP3082535A1')
        assert pub.title == 'AUTOMATIC FLUID DISPENSER'
        assert pub.priority_claims == ['201314137130', '2014071849']

    def test_epo(self):
        epo = Epo.objects.get('EP3082535A1')
        assert epo.title == 'AUTOMATIC FLUID DISPENSER'
        assert epo.status ==[{'description': 'Examination is in progress', 'code': '14', 'date': datetime.date(2018, 6, 15)}]