from .manager import PatentImageManager
from .model import Patent


def test_image_manager():
    result = PatentImageManager().get("10465445")
    assert result.pdf_url == "https://pdfpiw.uspto.gov/fdd/45/654/104/0.pdf"
    assert result.sections == {
        "Front Page": (1, 2),
        "Drawings": (3, 9),
        "Specifications": (10, 15),
        "Claims": (16, 18),
    }


def test_can_get_images():
    pat = Patent.objects.get(6103599)
    images = pat.images
    assert images.pdf_url == "https://pdfpiw.uspto.gov/fdd/99/035/061/0.pdf"
    assert images.sections == {
        "Claims": (10, 11),
        "Correction": (12, 12),
        "Drawings": (3, 6),
        "Front Page": (1, 2),
        "Specifications": (7, 9),
    }
