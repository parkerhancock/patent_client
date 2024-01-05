import pytest

from .global_dossier import GlobalDossierApi


@pytest.mark.anyio
async def test_get_dossier():
    result = await GlobalDossierApi.get_dossier("16123456")
    assert result["id"] == "16123456"


@pytest.mark.anyio
async def test_get_doc_list():
    result = await GlobalDossierApi.get_doc_list("US", "15644139", "A")
    assert len(result["docs"]) >= 34


@pytest.mark.anyio
async def test_get_document(tmp_path):
    result = await GlobalDossierApi.get_document("US", "201715644139.A", "JZBXRMELRXEAPX4", out_path=tmp_path)
    assert result.exists()
