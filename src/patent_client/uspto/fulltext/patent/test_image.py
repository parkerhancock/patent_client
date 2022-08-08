import pytest
from .manager import PatentImageManager
from .model import Patent

def test_can_get_images():
    pat = Patent.objects.get(6103599)
    images = pat.images
    assert images.pdf_url == "https://pdfpiw.uspto.gov/fdd/99/035/061/0.pdf"
    assert images.sections == [
        {"name": "Front Page", "start": 1, "end": 2},
        {"name": "Drawings", "start": 3, "end": 6},
        {"name": "Specifications", "start": 7, "end": 9},
        {"name": "Claims", "start": 10, "end": 11},
        {"name": "Correction", "start": 12, "end": 12},
    ]
