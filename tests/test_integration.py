import pytest

from ip import USApplication, PtabTrial, Inpadoc, Epo
from collections import OrderedDict

class TestIntegration():
    def test_can_get_trials(self):
        pat_no = '8118221'
        app = USApplication.objects.get(patent_number=pat_no)
        assert list(app.trials.values('trial_number')) == [OrderedDict([('trial_number', 'CBM2014-00102')]), OrderedDict([('trial_number', 'CBM2014-00103')]), OrderedDict([('trial_number', 'CBM2014-00194')]), OrderedDict([('trial_number', 'CBM2014-00199')]), OrderedDict([('trial_number', 'CBM2015-00015')]), OrderedDict([('trial_number', 'CBM2015-00117')]), OrderedDict([('trial_number', 'CBM2015-00126')]), OrderedDict([('trial_number', 'CBM2015-00130')])]
    
    def test_can_get_app_from_trials(self):
        trial = PtabTrial.objects.get('CBM2014-00102')
        print(trial.us_application.patent_title)
        assert trial.us_application.patent_title == 'DATA STORAGE AND ACCESS SYSTEMS'
    
    def test_can_get_inpadoc(self):
        pat_no = '8118221'
        app = USApplication.objects.get(patent_number=pat_no)
        print(app.inpadoc.title)
        assert app.inpadoc.title == 'Data storage and access systems'

    def test_can_get_us_app_from_inpadoc(self):
        app = Inpadoc.objects.get('US9231827B2')
        print(app.us_application.patent_title)
        assert app.us_application.patent_title == 'FORMALIZING, DIFFUSING AND ENFORCING POLICY ADVISORIES AND MONITORING POLICY COMPLIANCE IN THE MANAGEMENT OF NETWORKS'
