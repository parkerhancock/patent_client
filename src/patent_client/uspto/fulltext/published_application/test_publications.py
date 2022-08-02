from collections import OrderedDict

import pytest

from .model import PublishedApplication


class TestPublishedApplicationFullText:
    def test_fetch_publication(self):
        pub_no = 20_160_009_839
        pub = PublishedApplication.objects.get(pub_no)
        assert (
            pub.title
            == "POLYMER PRODUCTS AND MULTI-STAGE POLYMERIZATION PROCESSES FOR THE PRODUCTION THEREOF"
        )
        assert len(pub.abstract) == 651

    def test_publication_claims(self):
        pub_no = 20_160_009_839
        pub = PublishedApplication.objects.get(pub_no)
        assert len(pub.parsed_claims) == 25
        # Test Claim 1
        claim_1 = pub.parsed_claims[0]
        assert claim_1.number == 1
        assert len(claim_1.text) == 487
        assert len(claim_1.limitations) == 3
        assert claim_1.independent
        # Test Dependent Claim 2
        claim_2 = pub.parsed_claims[1]
        assert claim_2.number == 2
        assert claim_2.dependent

    def test_us_pub_20170370151(self):
        pub_no = 20_170_370_151
        pub = PublishedApplication.objects.get(pub_no)
        for i in range(6):
            assert pub.parsed_claims[i].text == f"{i+1}. (canceled)"
        assert (
            "A system to control directional drilling in borehole drilling for"
            in pub.parsed_claims[6].text
        )

    def test_search_classification(self):
        query = "CCL/166/308.1 AND APD/1/$/2015->1/$/2021"
        results = PublishedApplication.objects.filter(query=query)
        assert len(results) == 41
        assert results[25].publication_number == "20150354314"
        assert len(list(results[:15])) == 15
        counter = 0
        for i in results:
            counter += 1
        assert counter == 41

    def test_empty_search_result(self):
        query = "CCL/726/22 AND APD/19000101->20000619"
        results = PublishedApplication.objects.filter(query=query)
        assert len(results) == 0
        counter = 0
        for i in results:
            counter += 1
        assert counter == 0

    def test_nonstandard_claim_format(self):
        obj = PublishedApplication.objects.get("20170260839")
        assert (
            obj.parsed_claims[0].text[:39] == "1. A method of well ranging comprising:"
        )

    def test_can_get_images(self):
        pat = PublishedApplication.objects.get("20090150362")
        images = pat.images
        assert images.pdf_url == "https://pdfaiw.uspto.gov/fdd/62/2009/03/015/0.pdf"
        assert images.sections == [
            {'name': 'Front Page', 'start': 1, 'end': 1}, 
            {'name': 'Drawings', 'start': 2, 'end': 12}, 
            {'name': 'Specifications', 'start': 13, 'end': 23}, 
            {'name': 'Claims', 'start': 24, 'end': 24}
            ]
