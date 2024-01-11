import pytest

from .public_search import PublicSearchApi


class TestPublicSearch:
    @pytest.mark.anyio
    async def test_query(self):
        result = await PublicSearchApi.query('"B60N2/5628".CPC. AND @APD>="20210101"<=20210107')
        assert result["numFound"] == 1
        assert result["patents"][0]["guid"] == "US-20210122273-A1"

    @pytest.mark.anyio
    async def test_get_document(self):
        result = await PublicSearchApi.get_document("US-20210122273-A1", "US-PGPUB")
        assert result["guid"] == "US-20210122273-A1"

    @pytest.mark.anyio
    async def test_download_images(self, tmp_path):
        path = await PublicSearchApi.download_images("US-6103599-A", "uspat/US/06/103/599", "USPAT", 12, path=tmp_path)
        assert path.exists()
        assert path.stat().st_size > 0
