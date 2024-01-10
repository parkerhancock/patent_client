import pytest

from .cache import FileCache


def test_function(tmp_path):
    cache = FileCache(cache_dir=tmp_path)

    @cache
    def test_func(input: int):
        return input

    assert test_func(1) == 1
    assert test_func(1) == 1
    assert cache.statistics["3767363ac75d2e946883d7e76315073ab124dce5d77dabe9a7e359ffa0b1de12"] == 1


@pytest.mark.anyio
async def test_async_function(tmp_path):
    cache = FileCache(cache_dir=tmp_path)

    @cache
    async def test_func(input: int):
        return input

    assert await test_func(1) == 1
    assert await test_func(1) == 1
    assert cache.statistics["7cbc9be0cf97359f481efaac01b7b3cb0073d7116a7ea7e5b32adab7eecdd738"] == 1


def test_dsiable_cache(tmp_path):
    cache = FileCache(cache_dir=tmp_path)

    @cache
    def test_func(input: int):
        return input

    assert test_func(1) == 1
    cache.disable()
    assert test_func(1) == 1
    assert cache.statistics["3767363ac75d2e946883d7e76315073ab124dce5d77dabe9a7e359ffa0b1de12"] == 0
