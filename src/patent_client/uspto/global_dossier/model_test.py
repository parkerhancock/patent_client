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
        assert result.office_action_count == 2

    def test_us_download_docs(self, tmpdir):
        result = GlobalDossier.objects.get("16123456").applications[0].documents[0].download(tmpdir)
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

    def test_links(self):

        app = GlobalDossierApplication.objects.get("16123456")
        assert (
            app.us_application.patent_title
            == "LEARNING ASSISTANCE DEVICE, METHOD OF OPERATING LEARNING ASSISTANCE DEVICE, LEARNING ASSISTANCE PROGRAM, LEARNING ASSISTANCE SYSTEM, AND TERMINAL DEVICE"
        )
        # Broken links to Public Patent Search
        # assert (
        #    GlobalDossierApplication.objects.get("16123456").us_publication.patent_title
        #    == "Learning assistance device, method of operating learning assistance device, learning assistance program, learning assistance system, and terminal device"
        # )
        # assert (
        #    GlobalDossierApplication.objects.get("16123456").us_patent.patent_title
        #    == "Learning assistance device, method of operating learning assistance device, learning assistance program, learning assistance system, and terminal device"
        # )
        assert app.us_assignments.first().id == "46816-108"
        with pytest.raises(ValueError):
            GlobalDossierApplication.objects.get(publication="EP1000000").us_application
        # Broken links to Public Patent Search
        # with pytest.raises(ValueError):
        #    GlobalDossierApplication.objects.get(publication="EP1000000").us_publication
        # with pytest.raises(ValueError):
        #    GlobalDossierApplication.objects.get(publication="EP1000000").us_patent
        with pytest.raises(ValueError):
            GlobalDossierApplication.objects.get(publication="EP1000000").us_assignments

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
    @pytest.mark.asyncio
    async def test_us_lookup(self):
        result = await GlobalDossier.objects.aget("16123456")
        assert result.id == "16123456"

    @pytest.mark.asyncio
    async def test_us_lookup_docs(self):
        dossier = await GlobalDossier.objects.aget("16123456")
        result = dossier.applications[0].document_list
        assert result.office_action_count == 2

    @pytest.mark.asyncio
    async def test_us_download_docs(self, tmpdir):
        dossier = await GlobalDossier.objects.aget("16123456")
        result = dossier.applications[0].documents[0].download(tmpdir)
        assert result.exists()

    @pytest.mark.asyncio
    async def test_us_app_lookup(self):
        result = await GlobalDossierApplication.objects.aget("16123456")
        assert result.app_num == "16123456"
        assert isinstance(result, GlobalDossierApplication)

    @pytest.mark.asyncio
    async def test_us_app_lookup_docs(self):
        result = await GlobalDossierApplication.objects.aget("16123456")
        assert isinstance(result.document_list, DocumentList)
        assert isinstance(result.documents, list)
        assert isinstance(result.documents[0], Document)
        assert isinstance(result.office_actions, list)
        assert isinstance(result.office_actions[0], Document)

    @pytest.mark.asyncio
    async def test_links(self):
        app = await GlobalDossierApplication.objects.aget("16123456")
        assert (
            app.us_application.patent_title
            == "LEARNING ASSISTANCE DEVICE, METHOD OF OPERATING LEARNING ASSISTANCE DEVICE, LEARNING ASSISTANCE PROGRAM, LEARNING ASSISTANCE SYSTEM, AND TERMINAL DEVICE"
        )
        # Broken links to Public Patent Search
        # assert (
        #    GlobalDossierApplication.objects.get("16123456").us_publication.patent_title
        #    == "Learning assistance device, method of operating learning assistance device, learning assistance program, learning assistance system, and terminal device"
        # )
        # assert (
        #    GlobalDossierApplication.objects.get("16123456").us_patent.patent_title
        #    == "Learning assistance device, method of operating learning assistance device, learning assistance program, learning assistance system, and terminal device"
        # )
        assert app.us_assignments.first().id == "46816-108"
        with pytest.raises(ValueError):
            GlobalDossierApplication.objects.get(publication="EP1000000").us_application
        # Broken links to Public Patent Search
        # with pytest.raises(ValueError):
        #    GlobalDossierApplication.objects.get(publication="EP1000000").us_publication
        # with pytest.raises(ValueError):
        #    GlobalDossierApplication.objects.get(publication="EP1000000").us_patent
        with pytest.raises(ValueError):
            GlobalDossierApplication.objects.get(publication="EP1000000").us_assignments

    @pytest.mark.asyncio
    async def test_issue_99(self):
        app = await GlobalDossierApplication.objects.aget("16740760", type="application", office="US")
        assert app.app_num == "16740760"
        app = await GlobalDossierApplication.objects.aget("17193105")
        assert app.app_num == "17193105"
