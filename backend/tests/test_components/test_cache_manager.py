"""
Test CacheManager Component
"""
import pytest
import json
import time
from unittest.mock import AsyncMock, Mock, patch
from components.utils.cache_manager import CacheManager


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock()
    redis.delete = AsyncMock()
    redis.exists = AsyncMock(return_value=False)
    return redis


@pytest.fixture
def cache_manager():
    """Cache manager without Redis (in-memory mode)"""
    return CacheManager(redis_client=None, default_ttl=3600)


@pytest.fixture
def cache_manager_with_redis(mock_redis):
    """Cache manager with mocked Redis"""
    return CacheManager(redis_client=mock_redis, default_ttl=3600)


class TestCacheManagerInitialization:
    """Test CacheManager initialization"""
    
    def test_init_without_redis(self):
        """Should initialize with in-memory cache"""
        manager = CacheManager()
        
        assert manager.redis is None
        assert manager.default_ttl == 3600
        assert manager._local_cache == {}
    
    def test_init_with_redis(self, mock_redis):
        """Should initialize with Redis client"""
        manager = CacheManager(redis_client=mock_redis, default_ttl=7200)
        
        assert manager.redis == mock_redis
        assert manager.default_ttl == 7200
    
    def test_init_custom_ttl(self):
        """Should accept custom TTL"""
        manager = CacheManager(default_ttl=1800)
        
        assert manager.default_ttl == 1800


class TestKeyGeneration:
    """Test cache key generation"""
    
    def test_generate_key_simple(self, cache_manager):
        """Should generate namespaced key"""
        key = cache_manager._generate_key("web_crawl", "https://example.com")
        
        assert key == "cache:web_crawl:https://example.com"
    
    def test_generate_key_hashes_long_identifier(self, cache_manager):
        """Should hash identifiers longer than 100 chars"""
        long_id = "x" * 150
        key = cache_manager._generate_key("llm", long_id)
        
        assert key.startswith("cache:llm:")
        assert len(key.split(":")[-1]) == 64  # SHA256 hash length
    
    def test_generate_key_different_namespaces(self, cache_manager):
        """Should create unique keys for different namespaces"""
        key1 = cache_manager._generate_key("ns1", "id1")
        key2 = cache_manager._generate_key("ns2", "id1")
        
        assert key1 != key2
        assert "ns1" in key1
        assert "ns2" in key2


class TestInMemoryCache:
    """Test in-memory cache operations"""
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_manager):
        """Should store and retrieve value from in-memory cache"""
        await cache_manager.set("test", "key1", {"data": "value1"})
        result = await cache_manager.get("test", "key1")
        
        assert result == {"data": "value1"}
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_manager):
        """Should return None for missing key"""
        result = await cache_manager.get("test", "missing_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, cache_manager):
        """Should respect custom TTL"""
        await cache_manager.set("test", "key2", "value2", ttl=1)
        
        # Immediately available
        result = await cache_manager.get("test", "key2")
        assert result == "value2"
        
        # Wait for expiry
        time.sleep(1.1)
        result = await cache_manager.get("test", "key2")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_overwrite_existing_value(self, cache_manager):
        """Should overwrite existing cache value"""
        await cache_manager.set("test", "key3", "old_value")
        await cache_manager.set("test", "key3", "new_value")
        
        result = await cache_manager.get("test", "key3")
        assert result == "new_value"
    
    @pytest.mark.asyncio
    async def test_cache_complex_objects(self, cache_manager):
        """Should cache complex JSON-serializable objects"""
        complex_data = {
            "list": [1, 2, 3],
            "nested": {"key": "value"},
            "number": 42,
            "string": "test"
        }
        
        await cache_manager.set("test", "complex", complex_data)
        result = await cache_manager.get("test", "complex")
        
        assert result == complex_data


class TestRedisCache:
    """Test Redis-backed cache operations"""
    
    @pytest.mark.asyncio
    async def test_redis_get_success(self, cache_manager_with_redis, mock_redis):
        """Should retrieve value from Redis"""
        mock_redis.get.return_value = json.dumps({"data": "from_redis"})
        
        result = await cache_manager_with_redis.get("test", "redis_key")
        
        assert result == {"data": "from_redis"}
        mock_redis.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_redis_get_returns_none_when_missing(self, cache_manager_with_redis, mock_redis):
        """Should return None when Redis key doesn't exist"""
        mock_redis.get.return_value = None
        
        result = await cache_manager_with_redis.get("test", "missing")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_redis_set_success(self, cache_manager_with_redis, mock_redis):
        """Should store value in Redis with TTL"""
        data = {"test": "data"}
        
        await cache_manager_with_redis.set("test", "key", data, ttl=1800)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]
        assert call_args[0].startswith("cache:test:")
        assert call_args[1] == 1800
        assert json.loads(call_args[2]) == data
    
    @pytest.mark.asyncio
    async def test_redis_set_uses_default_ttl(self, cache_manager_with_redis, mock_redis):
        """Should use default TTL when not specified"""
        await cache_manager_with_redis.set("test", "key", "value")
        
        call_args = mock_redis.setex.call_args[0]
        assert call_args[1] == 3600  # Default TTL
    
    @pytest.mark.asyncio
    async def test_redis_error_falls_back_gracefully(self, cache_manager_with_redis, mock_redis):
        """Should handle Redis errors gracefully"""
        mock_redis.get.side_effect = Exception("Redis connection error")
        
        # Should not raise, returns None
        result = await cache_manager_with_redis.get("test", "key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_redis_set_error_silent_fail(self, cache_manager_with_redis, mock_redis):
        """Should silently fail on Redis set errors"""
        mock_redis.setex.side_effect = Exception("Redis error")
        
        # Should not raise
        await cache_manager_with_redis.set("test", "key", "value")
        
        # No assertion needed - just ensure no exception


class TestCacheInvalidation:
    """Test cache invalidation operations"""
    
    @pytest.mark.asyncio
    async def test_delete_from_memory(self, cache_manager):
        """Should delete value from in-memory cache"""
        await cache_manager.set("test", "key", "value")
        await cache_manager.delete("test", "key")
        
        result = await cache_manager.get("test", "key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_from_redis(self, cache_manager_with_redis, mock_redis):
        """Should delete value from Redis"""
        await cache_manager_with_redis.delete("test", "key")
        
        mock_redis.delete.assert_called_once()
        call_args = mock_redis.delete.call_args[0]
        assert call_args[0].startswith("cache:test:")
    
    @pytest.mark.asyncio
    async def test_clear_namespace(self, cache_manager):
        """Should clear all keys in namespace"""
        await cache_manager.set("test", "key1", "value1")
        await cache_manager.set("test", "key2", "value2")
        await cache_manager.set("other", "key3", "value3")
        
        await cache_manager.clear_namespace("test")
        
        # Test namespace cleared
        assert await cache_manager.get("test", "key1") is None
        assert await cache_manager.get("test", "key2") is None
        
        # Other namespace preserved
        assert await cache_manager.get("other", "key3") == "value3"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_non_serializable_value(self, cache_manager):
        """Should handle non-JSON-serializable values gracefully"""
        class CustomObject:
            pass
        
        # Should not raise, just skip caching
        await cache_manager.set("test", "key", CustomObject())
        
        result = await cache_manager.get("test", "key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_empty_string_identifier(self, cache_manager):
        """Should handle empty string identifiers"""
        await cache_manager.set("test", "", "value")
        result = await cache_manager.get("test", "")
        
        assert result == "value"
    
    @pytest.mark.asyncio
    async def test_unicode_keys(self, cache_manager):
        """Should handle unicode in keys"""
        await cache_manager.set("test", "键🔑", "value")
        result = await cache_manager.get("test", "键🔑")
        
        assert result == "value"
    
    @pytest.mark.asyncio
    async def test_large_values(self, cache_manager):
        """Should cache large values"""
        large_value = {"data": "x" * 10000}
        
        await cache_manager.set("test", "large", large_value)
        result = await cache_manager.get("test", "large")
        
        assert result == large_value
