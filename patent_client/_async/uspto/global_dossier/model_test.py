import pytest

from .model import Document, DocumentList, GlobalDossier, GlobalDossierApplication


class TestGlobalDossier:
    @pytest.mark.asyncio
    async def test_us_lookup(self):
        result = await GlobalDossier.objects.get("16123456")
        assert result.id == "16123456"

    @pytest.mark.asyncio
    async def test_us_lookup_docs(self):
        dossier = await GlobalDossier.objects.get("16123456")
        result = await dossier.applications[0].document_list
        assert len(result.office_action_docs) >= 2

    @pytest.mark.skip("issue in pytest-recording")
    @pytest.mark.asyncio
    async def test_us_download_docs(self, tmpdir):
        dossier = await GlobalDossier.objects.get("16123456")
        result = dossier.applications[0].documents[0].download(tmpdir)
        assert result.exists()

    @pytest.mark.asyncio
    async def test_us_app_lookup(self):
        result = await GlobalDossierApplication.objects.get("16123456")
        assert result.app_num == "16123456"
        assert isinstance(result, GlobalDossierApplication)

    @pytest.mark.asyncio
    async def test_us_app_lookup_docs(self):
        result = await GlobalDossierApplication.objects.get("16123456")
        document_list = await result.document_list
        documents = await result.documents
        office_actions = await result.office_actions
        assert isinstance(document_list, DocumentList)
        assert isinstance(documents, list)
        assert isinstance(documents[0], Document)
        assert isinstance(office_actions, list)
        assert isinstance(office_actions[0], Document)

    @pytest.mark.asyncio
    async def test_links(self):
        app = await GlobalDossierApplication.objects.get("16123456")
        us_application = await app.us_application
        assert (
            us_application.patent_title
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
        assignments = await app.us_assignments
        assert (await assignments.first()).id == "46816-108"
        with pytest.raises(ValueError):
            await (
                await GlobalDossierApplication.objects.get(publication="EP1000000")
            ).us_application
        # Broken links to Public Patent Search
        # with pytest.raises(ValueError):
        #    GlobalDossierApplication.objects.get(publication="EP1000000").us_publication
        # with pytest.raises(ValueError):
        #    GlobalDossierApplication.objects.get(publication="EP1000000").us_patent
        with pytest.raises(ValueError):
            await (
                await GlobalDossierApplication.objects.get(publication="EP1000000")
            ).us_assignments

    @pytest.mark.asyncio
    async def test_issue_99(self):
        app = await GlobalDossierApplication.objects.get(
            "16740760", type="application", office="US"
        )
        assert app.app_num == "16740760"
        app = await GlobalDossierApplication.objects.get("17193105")
        assert app.app_num == "17193105"
