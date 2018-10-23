import pytest
import os
import json

from patent_client.epo_ops import Epo, Inpadoc

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestInpadoc:
    def test_can_get_epo_pub(self):
        pub = Inpadoc.objects.get("CA2944968")
        assert pub.title == "WIRELINE POWER SUPPLY DURING ELECTRIC POWERED FRACTURING OPERATIONS"
        assert pub.publication == 'CA2944968A1'
        assert pub.applicants == ["US WELL SERVICES LLC"]
        assert pub.inventors == ["OEHRING, JARED, ", "HINDERLITER, BRANDON"]
        assert len(pub.full_text.description) == 35306
        assert pub.full_text.claims[:5] == [
            "1. A fracturing system comprising: a turbine generator having an electrical output; an electric motor that is in electrical communication with the electrical output; a fracturing pump that is driven by the electric motor; and a wireline system that is in electrical communication with the electrical output.",
            "2. The system of claim 1, further comprising a variable frequency drive connected to the electric motor to control the speed of the motor, wherein the variable frequency drive frequently performs electric motor diagnostics to prevent damage to the at least one electric motor.",
            "3. The system of claim 1, wherein the wireline system comprises a wireline tool that is disposable in a wellbore that is selected from the group consisting of a perforating gun, a plug, a formation logging tool, a cutting tool, a casing imaging tool, and combinations thereof.",
            "4. The system of claim 1, further comprising trailers that contain at least one power distribution panel that supplies power to the hydraulic fracturing equipment.",
            "5. The system of claim 4, where the trailers further contain receptacles for attaching cable to the hydraulic fracturing equipment and cables that can sustain the power draw of the turbines with three separate plugs for the three phase power.",
        ]
        assert pub.images.url == "http://ops.epo.org/rest-services/published-data/images/CA/2944968/A1/fullimage.pdf"
        assert pub.images.num_pages == 29
        assert pub.images.sections == {"ABSTRACT": 1, "CLAIMS": 22, "DESCRIPTION": 2, "DRAWINGS": 25}

    def test_can_download_full_images(self, tmpdir):
        pub = Inpadoc.objects.get("CA2944968")
        pub.images.download(path=str(tmpdir))
        assert os.listdir(str(tmpdir)) == ["CA2944968.pdf"]

    def test_can_handle_russian_cases(self):
        pub = Inpadoc.objects.get("RU2015124071")
        assert pub.title == "БУРОВОЕ ДОЛОТО ДЛЯ БУРИЛЬНОГО УСТРОЙСТВА"
        assert pub.cpc_class ==  [
                "E21B 7/064",
                "E21B 17/04",
                "E21B 47/01",
                "E21B 47/12",
                "E21B 7/067",
                "E21B 10/08",
                "E21B 10/567",
            ]
        assert pub.priority_claims == ["13/683,540", "US 2013/066560"]

    def test_can_get_ep_application(self):
        pubs = Inpadoc.objects.filter(application="EP13844704")
        assert len(pubs) == 2
        assert pubs[0].title == 'ATTITUDE REFERENCE FOR TIEBACK/OVERLAP PROCESSING'

    def test_pct(self):
        doc = Inpadoc.objects.get("PCT/US16/15853")
        assert doc.title == 'DUAL MODE TELEMETRY'

    def test_can_get_us_application(self):
        pub = Inpadoc.objects.get("US15915966", doc_type="application")
        assert pub.title  == "DEVICE AND METHOD FOR SURVEYING BOREHOLES OR ORIENTING DOWNHOLE ASSEMBLIES"


    def test_can_get_inpadoc_family(self):
        family = Inpadoc.objects.filter("EP13844704", doc_type="application")[0].family
        cases = [".".join([m.country, m.number, m.kind]) for m in family]
        assert cases == [
            "EP.2906782.A2",
            "EP.2906782.A4",
            "CA.2887530.A1",
            "CN.104968889.A",
            "RU.2015117646.A",
            "US.2014102795.A1",
            "US.9291047.B2",
            "US.2016245070.A1",
            "US.10047600.B2",
            "WO.2014059282.A2",
            "WO.2014059282.A3",
        ]

    def test_can_get_legal_status(self):
        pub = Inpadoc.objects.get("CA2300029C")
        print(pub.legal)
        assert pub.legal == [
            {
                "description": "EXAMINATION REQUEST",
                "explanation": "+",
                "code": "EEER",
                "date": "2005-02-03",
            }
        ]

    def test_can_search_inpadoc(self):
        results = Inpadoc.objects.search('pa="Scientific Drilling"')
        assert len(results) == 206
        assert results.values('title')[:10] == [{'title': 'SUB-SURFACE ELECTROMAGNETIC TELEMETRY SYSTEMS AND METHODS'},
 {'title': 'DEVICE AND METHOD FOR SURVEYING BOREHOLES OR ORIENTING DOWNHOLE '
           'ASSEMBLIES'},
 {'title': 'DEVICE AND METHOD FOR SURVEYING BOREHOLES OR ORIENTING DOWNHOLE '
           'ASSEMBLIES'},
 {'title': 'METHOD FOR IMPROVING SURVEY MEASUREMENT DENSITY ALONG A BOREHOLE'},
 {'title': 'LOGGING-WHILE-DRILLING SPECTRAL AND AZIMUTHAL GAMMA RAY APPARATUS '
           'AND METHODS'},
 {'title': 'DOWNHOLE MWD SIGNAL ENHANCEMENT, TRACKING, AND DECODING'},
 {'title': 'LOGGING-WHILE-DRILLING SPECTRAL AND AZIMUTHAL GAMMA RAY APPARATUS '
           'AND METHODS'},
 {'title': 'TUMBLE GYRO SURVEYOR'},
 {'title': 'SURFACE COIL FOR WELLBORE POSITIONING'},
 {'title': 'COHERENT MEASUREMENT METHOD FOR DOWNHOLE APPLICATIONS'}]
        #us_cases = results.filter(publication__country='US')[:5]
        #from pprint import pprint
        #pprint(us_cases)
        #assert False


class TestEpoRegister:
    def test_can_get_epo_data(self):
        pub = Epo.objects.get("EP3221665A1")
        assert pub.status == [
            {
                "description": "Request for examination was made",
                "code": "15",
                "date": "20170825",
            },
            {
                "description": "The international publication has been made",
                "code": "17",
                "date": "20170512",
            },
        ]
        assert pub.bib_data == {
            "applicants": [
                {
                    "address": "16701 Greenspoint Park Dr.\n"
                    "Suite 200\n"
                    "Houston, TX 77060\n"
                    "US",
                    "name": "Scientific Drilling International, Inc.",
                }
            ],
            "applications": [
                {"country": "EP", "date": "20151119", "number": "15860753"},
                {"country": "WO", "number": "WO2015US61659"},
            ],
            "citations": [
                {
                    "category": "Y",
                    "citation": {"country": "US", "number": "2014007646"},
                    "office": "EP",
                    "phase": "international-search-report",
                    "relevant_passages": "(RODNEY PAUL F [US], et al) [Y] 1-43 * "
                    "entire document *;",
                },
                {
                    "category": "Y",
                    "citation": {"country": "US", "number": "4987684"},
                    "office": "EP",
                    "phase": "international-search-report",
                    "relevant_passages": "(ANDREAS RONALD D [US], et al) [Y] 1-14, "
                    "33-43 * entire document *;",
                },
                {
                    "category": "Y",
                    "citation": {"country": "US", "number": "2008230273"},
                    "office": "EP",
                    "phase": "international-search-report",
                    "relevant_passages": "(BROOKS ANDREW G [US]) [Y] 2-32, 35-38, "
                    "41, 43 * entire document *;",
                },
                {
                    "category": "Y",
                    "citation": {"country": "US", "number": "2007242042"},
                    "office": "EP",
                    "phase": "international-search-report",
                    "relevant_passages": "(KELLY MICHAEL B [US]) [Y] 23, 24 * "
                    "entire document *;",
                },
                {
                    "category": "Y",
                    "citation": {"country": "US", "number": "5039944"},
                    "office": "EP",
                    "phase": "international-search-report",
                    "relevant_passages": "(KIM BORIS F [US], et al) [Y] 25, 26 * "
                    "entire document *;",
                },
                {
                    "category": "A",
                    "citation": {"country": "US", "number": "2003220743"},
                    "office": "EP",
                    "phase": "international-search-report",
                    "relevant_passages": "(VAN STEENWYK DONALD H [US], et al) [A] "
                    "1-43 * entire document *",
                },
            ],
            "designated_states": [
                "EP",
                "AL",
                "AT",
                "BE",
                "BG",
                "CH",
                "CY",
                "CZ",
                "DE",
                "DK",
                "EE",
                "ES",
                "FI",
                "FR",
                "GB",
                "GR",
                "HR",
                "HU",
                "IE",
                "IS",
                "IT",
                "LI",
                "LT",
                "LU",
                "LV",
                "MC",
                "MK",
                "MT",
                "NL",
                "NO",
                "PL",
                "PT",
                "RO",
                "RS",
                "SE",
                "SI",
                "SK",
                "SM",
                "TR",
            ],
            "filing_language": "en",
            "intl_class": ["G01C25/00, E21B47/024"],
            "inventors": [
                {
                    "address": "c/o Scientific Drilling International Inc.\n"
                    "16701 Greenspoint Park Dr.\n"
                    "Suite 200\n"
                    "Houston, TX 77060\n"
                    "US",
                    "name": "VAN STEENWYK, Brett",
                }
            ],
            "priority_claims": [
                {"date": "20141119", "kind": "national", "number": "201462081944P"}
            ],
            "publications": [
                {
                    "country": "WO",
                    "date": "20160526",
                    "kind": "A1",
                    "number": "2016081758",
                },
                {
                    "country": "EP",
                    "date": "20170927",
                    "kind": "A1",
                    "number": "3221665",
                },
            ],
            "status": [
                {
                    "code": "15",
                    "date": "20170825",
                    "description": "Request for examination was made",
                },
                {
                    "code": "17",
                    "date": "20170512",
                    "description": "The international publication has been made",
                },
            ],
            "title": "INERTIAL CAROUSEL POSITIONING",
        }
        assert pub.procedural_steps == [{'code': 'RFEE',
            'date': '20171113',
            'description': 'Renewal fee payment - 03',
            'phase': 'undefined'},
            {'code': 'FFEE',
            'date': '20170511',
            'description': 'Payment of national basic fee',
            'phase': 'entry-regional-phase'},
            {'code': 'SFEE',
            'date': '20170511',
            'description': 'Payment of the fee for supplementary search',
            'phase': 'entry-regional-phase'},
            {'code': 'DEST',
            'date': '20170511',
            'description': 'Payment of the first designation fee',
            'phase': 'entry-regional-phase'},
            {'code': 'EXAM_PCT',
            'date': '20170511',
            'description': 'Payment of the fee for examination',
            'phase': 'entry-regional-phase'},
            {'code': 'EXAM52',
            'date': '20170511',
            'description': 'Date on which the examining division has become responsible',
            'phase': 'examination'},
            {'code': 'ABEX',
            'date': '20171229',
            'description': 'Amendments - (claims and/or description)',
            'phase': 'examination'},
            {'code': 'PREX',
            'date': '20160819',
            'description': 'Preliminary examination - PCT II',
            'phase': 'international-examination'},
            {'code': 'PROL',
            'date': None,
            'description': 'Language of the procedure - en',
            'phase': 'examination'},
            {'code': 'ISAT',
            'date': None,
            'description': 'International searching authority - US',
            'phase': 'entry-regional-phase'}]

