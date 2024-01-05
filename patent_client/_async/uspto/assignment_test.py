import pytest

from .assignment import AssignmentApi


@pytest.mark.anyio
async def test_lookup():
    tree = await AssignmentApi.lookup("Apple", "OwnerName")
    assert len(tree.findall(".//doc")) == 8


@pytest.mark.anyio
async def test_download_pdf(tmp_path):
    path = tmp_path / "test.pdf"
    await AssignmentApi.download_pdf("44101", "610", path)
    assert path.exists()
    assert path.stat().st_size > 0
