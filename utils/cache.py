"""Cache management module."""

import hashlib
import os
import pickle
import time
from functools import lru_cache
from typing import Any

from utils.config import Config
from utils.logger import Logger


class CacheManager:
    """Cache manager for storing and retrieving cached data.

    Provides file-based caching with expiration support.
    """

    def __init__(self, cache_dir: str = None):
        """Initialize cache manager.

        Args:
            cache_dir: Directory for cache files. If None, uses Config.CACHE_DIR
        """
        self.cache_dir = cache_dir or Config.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def get(self, key: str, expire: int = None) -> Any:
        """Get cached value.

        Args:
            key: Cache key
            expire: Expiration time in seconds. If None, uses Config.CACHE_EXPIRE

        Returns:
            Cached value, or None if not found or expired
        """
        if expire is None:
            expire = Config.CACHE_EXPIRE

        cache_file = self._get_cache_file(key)
        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)

            if time.time() - data['timestamp'] > expire:
                os.remove(cache_file)
                return None

            return data['value']
        except (pickle.PickleError, EOFError, KeyError):
            # Corrupted cache file, remove it
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_file = self._get_cache_file(key)
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'value': value,
                'timestamp': time.time()
            }, f)

    def clear(self, key: str = None) -> None:
        """Clear cached value.

        Args:
            key: Cache key to clear. If None, clears all cache
        """
        if key:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, file))

    def _get_cache_file(self, key: str) -> str:
        """Get cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Cache file path
        """
        # Hash the key to create a valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")


@lru_cache(maxsize=100)
def cached_get(cache_manager: CacheManager, key: str) -> Any:
    """LRU cached version of cache get (in-memory cache).

    Args:
        cache_manager: Cache manager instance
        key: Cache key

    Returns:
        Cached value
    """
    return cache_manager.get(key)