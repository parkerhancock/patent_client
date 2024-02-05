import pytest

from .manager import DocumentListManager
from .model import Document
from .model import DocumentList
from .model import GlobalDossier
from .model import GlobalDossierApplication


class TestGlobalDossier:
    def test_us_lookup(self):
        result = GlobalDossier.objects.get("16123456")
        assert result.id == "16123456"

    def test_us_lookup_docs(self):
        result = GlobalDossier.objects.get("16123456").applications[0].document_list
        assert len(result.office_action_docs) >= 2
        assert result.office_action_count >= 2
        assert len(result.office_action_docs) == result.office_action_count

    def test_us_download_docs(self, tmp_path):
        result = GlobalDossier.objects.get("16123456").applications[0].documents[0].download(tmp_path)
        assert result.exists()

    def test_us_app_lookup(self):
        result = GlobalDossierApplication.objects.get("16123456")
        assert result.app_num == "16123456"
        assert isinstance(result, GlobalDossierApplication)

    def test_us_app_lookup_docs(self):
        result = GlobalDossierApplication.objects.get("16123456")
        assert isinstance(result.document_list, DocumentList)
        assert isinstance(result.documents, list)
        assert isinstance(result.documents[0], Document)
        assert isinstance(result.office_actions, list)
        assert isinstance(result.office_actions[0], Document)

    def test_raises_errors_on_db_methods(self):
        with pytest.raises(NotImplementedError):
            GlobalDossier.objects.filter("something")
        with pytest.raises(NotImplementedError):
            GlobalDossier.objects.order_by("something")
        with pytest.raises(NotImplementedError):
            GlobalDossier.objects.limit("something")
        with pytest.raises(NotImplementedError):
            GlobalDossier.objects.offset("something")
        with pytest.raises(NotImplementedError):
            DocumentListManager().filter("something")
        with pytest.raises(NotImplementedError):
            DocumentListManager().order_by("something")
        with pytest.raises(NotImplementedError):
            DocumentListManager().limit("something")
        with pytest.raises(NotImplementedError):
            DocumentListManager().offset("something")

    def test_issue_99(self):
        app = GlobalDossierApplication.objects.get("16740760", type="application", office="US")
        assert app.app_num == "16740760"
        app = GlobalDossierApplication.objects.get("17193105")
        assert app.app_num == "17193105"


class TestGlobalDossierAsync:
    @pytest.mark.anyio
    async def test_us_lookup(self):
        result = await GlobalDossier.objects.aget("16123456")
        assert result.id == "16123456"

    @pytest.mark.anyio
    async def test_us_lookup_docs(self):
        dossier = await GlobalDossier.objects.aget("16123456")
        result = dossier.applications[0].document_list
        assert result.office_action_count >= 2

    @pytest.mark.anyio
    async def test_us_download_docs(self, tmpdir):
        dossier = await GlobalDossier.objects.aget("16123456")
        result = dossier.applications[0].documents[0].download(tmpdir)
        assert result.exists()

    @pytest.mark.anyio
    async def test_us_app_lookup(self):
        result = await GlobalDossierApplication.objects.aget("16123456")
        assert result.app_num == "16123456"
        assert isinstance(result, GlobalDossierApplication)

    @pytest.mark.anyio
    async def test_us_app_lookup_docs(self):
        result = await GlobalDossierApplication.objects.aget("16123456")
        assert isinstance(result.document_list, DocumentList)
        assert isinstance(result.documents, list)
        assert isinstance(result.documents[0], Document)
        assert isinstance(result.office_actions, list)
        assert isinstance(result.office_actions[0], Document)

    @pytest.mark.anyio
    async def test_issue_99(self):
        app = await GlobalDossierApplication.objects.aget("16740760", type="application", office="US")
        assert app.app_num == "16740760"
        app = await GlobalDossierApplication.objects.aget("17193105")
        assert app.app_num == "17193105"
