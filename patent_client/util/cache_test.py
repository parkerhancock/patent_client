import pytest

from .cache import FileCache


def test_function(tmp_path):
    cache = FileCache(cache_dir=tmp_path)

    @cache
    def test_func(input: int):
        return input

    assert test_func(1) == 1
    assert test_func(1) == 1
    assert cache.statistics["2a5394dcfdf8c471772a9f5f81360a6e5c58140f2709c319a416bd22d05407e7"] == 1


@pytest.mark.anyio
async def test_async_function(tmp_path):
    cache = FileCache(cache_dir=tmp_path)

    @cache
    async def test_func(input: int):
        return input

    assert await test_func(1) == 1
    assert await test_func(1) == 1
    assert cache.statistics["1ca93912fc0db523d3837c4e900198a45bf080fc5ae9fd53c7f6b22cd1d026e4"] == 1


def test_dsiable_cache(tmp_path):
    cache = FileCache(cache_dir=tmp_path)

    @cache
    def test_func(input: int):
        return input

    assert test_func(1) == 1
    cache.disable()
    assert test_func(1) == 1
    assert len(cache.statistics) == 0
