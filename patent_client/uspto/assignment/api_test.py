import pytest

from .api import AssignmentAsyncApi


class TestAssignmentAsyncApi:
    @pytest.mark.anyio
    async def test_lookup(self):
        result = await AssignmentAsyncApi.lookup("Apple", "OwnerName")
        assert len(result.docs) == 8

    @pytest.mark.anyio
    async def test_download_pdf(self, tmpdir):
        result = await AssignmentAsyncApi.download_pdf("44101", "0610", path=tmpdir)
        assert result.exists()
