import pytest

from .manager import GlobalDossierDocument
from .model import Document
from .model import DocumentList
from .model import GlobalDossier
from .model import GlobalDossierApplication


def test_us_lookup():
    result = GlobalDossier.objects.get("16123456")
    assert result.id == "16123456"


def test_us_lookup_docs():
    result = GlobalDossier.objects.get("16123456").applications[0].document_list
    assert result.office_action_count == 2


def test_us_download_docs(tmpdir):
    result = GlobalDossier.objects.get("16123456").applications[0].documents[0].download(tmpdir)
    assert result.exists()


def test_us_app_lookup():
    result = GlobalDossierApplication.objects.get("16123456")
    assert result.app_num == "16123456"
    assert isinstance(result, GlobalDossierApplication)


def test_us_app_lookup_docs():
    result = GlobalDossierApplication.objects.get("16123456")
    assert isinstance(result.document_list, DocumentList)
    assert isinstance(result.documents, list)
    assert isinstance(result.documents[0], Document)
    assert isinstance(result.office_actions, list)
    assert isinstance(result.office_actions[0], Document)


def test_links():
    assert (
        GlobalDossierApplication.objects.get("16123456").us_application.patent_title
        == "LEARNING ASSISTANCE DEVICE, METHOD OF OPERATING LEARNING ASSISTANCE DEVICE, LEARNING ASSISTANCE PROGRAM, LEARNING ASSISTANCE SYSTEM, AND TERMINAL DEVICE"
    )
    assert (
        GlobalDossierApplication.objects.get("16123456").us_publication.patent_title
        == "Learning assistance device, method of operating learning assistance device, learning assistance program, learning assistance system, and terminal device"
    )
    assert (
        GlobalDossierApplication.objects.get("16123456").us_patent.patent_title
        == "Learning assistance device, method of operating learning assistance device, learning assistance program, learning assistance system, and terminal device"
    )
    assert GlobalDossierApplication.objects.get("16123456").us_assignments.first().id == "46816-108"
    with pytest.raises(ValueError):
        GlobalDossierApplication.objects.get(publication="EP1000000").us_application
    with pytest.raises(ValueError):
        GlobalDossierApplication.objects.get(publication="EP1000000").us_publication
    with pytest.raises(ValueError):
        GlobalDossierApplication.objects.get(publication="EP1000000").us_patent
    with pytest.raises(ValueError):
        GlobalDossierApplication.objects.get(publication="EP1000000").us_assignments


def test_raises_errors_on_db_methods():
    with pytest.raises(NotImplementedError):
        GlobalDossier.objects.filter("something")
    with pytest.raises(NotImplementedError):
        GlobalDossier.objects.order_by("something")
    with pytest.raises(NotImplementedError):
        GlobalDossier.objects.limit("something")
    with pytest.raises(NotImplementedError):
        GlobalDossier.objects.offset("something")
    with pytest.raises(NotImplementedError):
        GlobalDossierDocument().filter("something")
    with pytest.raises(NotImplementedError):
        GlobalDossierDocument().order_by("something")
    with pytest.raises(NotImplementedError):
        GlobalDossierDocument().limit("something")
    with pytest.raises(NotImplementedError):
        GlobalDossierDocument().offset("something")
