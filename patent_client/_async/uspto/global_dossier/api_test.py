from pathlib import Path

import pytest

from .api import GlobalDossierApi
from .model import DocumentList, GlobalDossier


@pytest.mark.asyncio
async def test_get_file():
    api = GlobalDossierApi()
    doc_number = "16740760"
    type_code = "application"
    office_code = "US"
    response = await api.get_file(doc_number, type_code, office_code)
    assert isinstance(response, GlobalDossier)
    assert response.country == "US"
    assert response.id == "16740760"


@pytest.mark.asyncio
async def test_get_doc_list():
    api = GlobalDossierApi()
    country = "US"
    doc_number = "16740760"
    kind_code = "A"
    response = await api.get_doc_list(country, doc_number, kind_code)
    assert isinstance(response, DocumentList)
    assert len(response.docs) > 0


@pytest.mark.asyncio
async def test_get_document(tmp_path: Path):
    api = GlobalDossierApi()
    country = "US"
    doc_number = "201816123456.A"
    document_id = "KJM2MWIEDFLYX10"
    out_path = tmp_path / "test_document.pdf"
    await api.get_document(country, doc_number, document_id, out_path)
    assert out_path.exists()
    assert out_path.stat().st_size > 0
