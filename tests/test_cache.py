"""Tests for cache manager."""

import os
import time
import tempfile

import pytest

from utils.cache import CacheManager


def test_cache_manager_creation(tmp_path):
    """Test CacheManager can be created"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))
    assert cache.cache_dir == str(cache_dir)
    assert os.path.exists(cache_dir)


def test_cache_set_and_get(tmp_path):
    """Test cache can set and get values"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 42})
    result = cache.get("test_key")

    assert result is not None
    assert result["value"] == 42


def test_cache_expire(tmp_path):
    """Test cache respects expiration time"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 42})
    # Set a very short expiration
    result = cache.get("test_key", expire=0.1)  # 0.1 seconds

    assert result is not None

    # Wait for expiration
    time.sleep(0.15)

    result = cache.get("test_key", expire=0.1)
    assert result is None


def test_cache_clear(tmp_path):
    """Test cache can be cleared"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 42})
    assert cache.get("test_key") is not None

    cache.clear("test_key")
    assert cache.get("test_key") is None


def test_cache_clear_all(tmp_path):
    """Test cache can clear all keys"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key1", {"value": 1})
    cache.set("test_key2", {"value": 2})

    cache.clear()  # Clear all

    assert cache.get("test_key1") is None
    assert cache.get("test_key2") is None


def test_cache_get_nonexistent(tmp_path):
    """Test getting nonexistent key returns None"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    result = cache.get("nonexistent_key")
    assert result is None


def test_cache_various_types(tmp_path):
    """Test cache can store various Python types"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    # Test string
    cache.set("string_key", "hello")
    assert cache.get("string_key") == "hello"

    # Test int
    cache.set("int_key", 123)
    assert cache.get("int_key") == 123

    # Test float
    cache.set("float_key", 3.14)
    assert cache.get("float_key") == 3.14

    # Test list
    cache.set("list_key", [1, 2, 3])
    assert cache.get("list_key") == [1, 2, 3]

    # Test dict
    cache.set("dict_key", {"a": 1, "b": 2})
    assert cache.get("dict_key") == {"a": 1, "b": 2}


def test_cache_file_hashing(tmp_path):
    """Test that keys are properly hashed to filenames"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("simple_key", "value1")
    cache.set("another_key", "value2")

    # Both should create files with different names
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.cache')]
    assert len(cache_files) == 2

    # And they should be different
    assert cache_files[0] != cache_files[1]


def test_cache_corrupted_file(tmp_path):
    """Test that corrupted cache files are handled gracefully"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    # Create a corrupted cache file
    cache_file = cache._get_cache_file("corrupted_key")
    with open(cache_file, 'w') as f:
        f.write("corrupted data")

    # Should return None and remove the file
    result = cache.get("corrupted_key")
    assert result is None
    assert not os.path.exists(cache_file)


def test_cache_overwrite(tmp_path):
    """Test that overwriting a cache key works"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 1})
    assert cache.get("test_key")["value"] == 1

    cache.set("test_key", {"value": 2})
    assert cache.get("test_key")["value"] == 2


def test_cache_default_dir():
    """Test that cache uses default directory from Config"""
    cache = CacheManager()
    assert cache.cache_dir == "data/cache"
    assert os.path.exists(cache.cache_dir)


def test_cached_get_function(tmp_path):
    """Test the cached_get function with lru_cache"""
    from utils.cache import cached_get

    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 42})

    # First call
    result1 = cached_get(cache, "test_key")
    assert result1["value"] == 42

    # Second call should use in-memory cache
    result2 = cached_get(cache, "test_key")
    assert result2["value"] == 42