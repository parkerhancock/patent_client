import datetime
import inspect
import pickle
from collections import defaultdict
from hashlib import blake2b
from pathlib import Path


class FileCache:
    """A file-based function cache that can be used as a decorator.
    Uses the full path of a function and passed arguments as a cache key
    and stores the return value of the function in a file.

    The decorator can work with both async functions and regular functions.

    :param cache_dir: The directory to store cached files in.
    :param ttl: The time-to-live for cached files in seconds.
    """

    def __init__(self, cache_dir: str, ttl: int = 60 * 60 * 24 * 3):
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.enabled = True
        self.statistics_file = self.cache_dir / "statistics.pkl"
        if self.statistics_file.exists():
            try:
                with self.statistics_file.open("rb") as f:
                    self.statistics = defaultdict(int, pickle.load(f))
            except EOFError:
                self.statistics = defaultdict(int)
        else:
            self.statistics = defaultdict(int)

    def __call__(self, func):
        def sync_wrapper(*args, **kwargs):
            if self.enabled is False:
                return func(*args, **kwargs)
            key = self._get_key(func, args, kwargs)
            path = (self.cache_dir / key).with_suffix(".pkl")
            if path.exists():
                if (
                    datetime.datetime.now() - datetime.datetime.fromtimestamp(path.stat().st_mtime)
                ).total_seconds() < self.ttl:
                    try:
                        with open(path, "rb") as f:
                            result = pickle.load(f)
                            self.statistics[key] += 1
                            return result
                    except EOFError:
                        path.unlink()

            value = func(*args, **kwargs)
            with open(path, "wb") as f:
                pickle.dump(value, f)
            return value

        async def async_wrapper(*args, **kwargs):
            if self.enabled is False:
                return await func(*args, **kwargs)
            key = self._get_key(func, args, kwargs)
            path = (self.cache_dir / key).with_suffix(".pkl")
            if path.exists():
                if (
                    datetime.datetime.now() - datetime.datetime.fromtimestamp(path.stat().st_mtime)
                ).total_seconds() < self.ttl:
                    try:
                        with open(path, "rb") as f:
                            result = pickle.load(f)
                            self.statistics[key] += 1
                            return result
                    except EOFError:
                        path.unlink()
            value = await func(*args, **kwargs)
            with open(path, "wb") as f:
                pickle.dump(value, f)
            return value

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    def __del__(self):
        with self.statistics_file.open("wb") as f:
            pickle.dump(dict(self.statistics), f)

    def _get_key(self, func, args, kwargs):
        key = str(func.__module__) + str(func.__qualname__) + str(args) + str(kwargs)
        hash = blake2b(key.encode(), digest_size=32).hexdigest()
        return hash

    def disable(self):
        """Disable the cache."""
        self.enabled = False

    def enable(self):
        """Enable the cache."""
        self.enabled = True
