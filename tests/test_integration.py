from collections import OrderedDict

import pytest
from patent_client import Inpadoc
from patent_client import PtabTrial
from patent_client import USApplication, Assignment

from patent_client.epo_ops.ops import OpenPatentServicesConnector
from patent_client.epo_ops.models import InpadocImages
from patent_client.uspto_peds import USApplicationManager
from patent_client.uspto_ptab import PtabManager
from patent_client.uspto_assignments import Assignment, AssignmentManager
PtabManager.test_mode = True
USApplicationManager.test_mode = True
InpadocImages.test_mode = True
OpenPatentServicesConnector.test_mode = True
AssignmentManager.test_mode = True



class TestIntegration:
    def test_can_get_trials(self):
        pat_no = "8118221"
        app = USApplication.objects.get(patent_number=pat_no)
        assert list(app.trials.values("trial_number")) == [
            OrderedDict([("trial_number", "CBM2014-00102")]),
            OrderedDict([("trial_number", "CBM2014-00103")]),
            OrderedDict([("trial_number", "CBM2014-00194")]),
            OrderedDict([("trial_number", "CBM2014-00199")]),
            OrderedDict([("trial_number", "CBM2015-00015")]),
            OrderedDict([("trial_number", "CBM2015-00117")]),
            OrderedDict([("trial_number", "CBM2015-00126")]),
            OrderedDict([("trial_number", "CBM2015-00130")]),
        ]

    def test_can_get_app_from_trials(self):
        trial = PtabTrial.objects.get("CBM2014-00102")
        print(trial.us_application.patent_title)
        assert trial.us_application.patent_title == "DATA STORAGE AND ACCESS SYSTEMS"

    def test_can_get_inpadoc(self):
        pat_no = "8118221"
        app = USApplication.objects.get(patent_number=pat_no)
        assert app.inpadoc[0].document.title == "Data Storage and Access Systems"

    def test_can_get_us_app_from_inpadoc(self):
        app = Inpadoc.objects.get("US9231827B2")
        assert (
            app.us_application.patent_title
            == "FORMALIZING, DIFFUSING AND ENFORCING POLICY ADVISORIES AND MONITORING POLICY COMPLIANCE IN THE MANAGEMENT OF NETWORKS"
        )

    def test_can_get_assignments_from_application(self):
        app = USApplication.objects.get("13842218")
        assert list(app.assignments.values_list("id", flat=True)) == [
            "36385-377",
            "36408-10",
            "37418-226",
        ]
    
    def test_can_get_applications_from_assignment(self):
        assignments = Assignment.objects.filter(assignee="Covar Applied")
        assignment = assignments[0]
        assert assignment.us_applications[0].appl_id == '15274746'
