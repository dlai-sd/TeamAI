"""
Test RateLimiter Component
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch
from components.utils.rate_limiter import RateLimiter


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis = AsyncMock()
    
    # Mock pipeline
    pipe = AsyncMock()
    pipe.zremrangebyscore = Mock(return_value=pipe)
    pipe.zcard = Mock(return_value=pipe)
    pipe.zadd = Mock(return_value=pipe)
    pipe.expire = Mock(return_value=pipe)
    pipe.execute = AsyncMock(return_value=[None, 0, None, None])
    
    redis.pipeline = Mock(return_value=pipe)
    redis.zrem = AsyncMock()
    
    return redis


@pytest.fixture
def rate_limiter():
    """Rate limiter without Redis (in-memory mode)"""
    return RateLimiter(redis_client=None, default_rate=10, default_period=60)


@pytest.fixture
def rate_limiter_with_redis(mock_redis):
    """Rate limiter with mocked Redis"""
    return RateLimiter(redis_client=mock_redis, default_rate=10, default_period=60)


class TestRateLimiterInitialization:
    """Test RateLimiter initialization"""
    
    def test_init_without_redis(self):
        """Should initialize with in-memory buckets"""
        limiter = RateLimiter()
        
        assert limiter.redis is None
        assert limiter.default_rate == 10
        assert limiter.default_period == 60
        assert limiter._local_buckets == {}
    
    def test_init_with_redis(self, mock_redis):
        """Should initialize with Redis client"""
        limiter = RateLimiter(redis_client=mock_redis, default_rate=20, default_period=120)
        
        assert limiter.redis == mock_redis
        assert limiter.default_rate == 20
        assert limiter.default_period == 120
    
    def test_init_custom_defaults(self):
        """Should accept custom default rate and period"""
        limiter = RateLimiter(default_rate=100, default_period=3600)
        
        assert limiter.default_rate == 100
        assert limiter.default_period == 3600


class TestInMemoryRateLimiting:
    """Test in-memory rate limiting"""
    
    @pytest.mark.asyncio
    async def test_acquire_within_limit(self, rate_limiter):
        """Should allow requests within rate limit"""
        # Set low rate for testing
        limiter = RateLimiter(default_rate=3, default_period=10)
        
        # Should allow first 3 requests
        assert await limiter.acquire("test_key") is True
        assert await limiter.acquire("test_key") is True
        assert await limiter.acquire("test_key") is True
    
    @pytest.mark.asyncio
    async def test_acquire_exceeds_limit(self, rate_limiter):
        """Should reject requests exceeding rate limit"""
        limiter = RateLimiter(default_rate=2, default_period=10)
        
        # First 2 should pass
        assert await limiter.acquire("test_key") is True
        assert await limiter.acquire("test_key") is True
        
        # Third should be rate limited
        assert await limiter.acquire("test_key") is False
    
    @pytest.mark.asyncio
    async def test_sliding_window_expiry(self, rate_limiter):
        """Should allow requests after window expires"""
        limiter = RateLimiter(default_rate=2, default_period=1)
        
        # Use up limit
        await limiter.acquire("test_key")
        await limiter.acquire("test_key")
        
        # Should be rate limited
        assert await limiter.acquire("test_key") is False
        
        # Wait for window to slide
        await asyncio.sleep(1.1)
        
        # Should be allowed again
        assert await limiter.acquire("test_key") is True
    
    @pytest.mark.asyncio
    async def test_different_keys_independent(self, rate_limiter):
        """Should track different keys independently"""
        limiter = RateLimiter(default_rate=1, default_period=10)
        
        # Each key gets its own bucket
        assert await limiter.acquire("key1") is True
        assert await limiter.acquire("key2") is True
        
        # But each is limited independently
        assert await limiter.acquire("key1") is False
        assert await limiter.acquire("key2") is False
    
    @pytest.mark.asyncio
    async def test_custom_rate_and_period(self, rate_limiter):
        """Should accept custom rate and period per request"""
        # Allow 5 requests per 2 seconds
        limiter = RateLimiter()
        
        for i in range(5):
            result = await limiter.acquire("test", rate=5, period=2)
            assert result is True
        
        # 6th should be rejected
        result = await limiter.acquire("test", rate=5, period=2)
        assert result is False


class TestRedisRateLimiting:
    """Test Redis-backed rate limiting"""
    
    @pytest.mark.asyncio
    async def test_redis_acquire_success(self, rate_limiter_with_redis, mock_redis):
        """Should acquire token from Redis"""
        # Mock: 5 requests in window (under limit of 10)
        pipe = mock_redis.pipeline.return_value
        pipe.execute.return_value = [None, 5, None, None]
        
        result = await rate_limiter_with_redis.acquire("api_key")
        
        assert result is True
        mock_redis.pipeline.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_redis_acquire_rate_limited(self, rate_limiter_with_redis, mock_redis):
        """Should reject when rate limit exceeded"""
        # Mock: 10 requests in window (at limit)
        pipe = mock_redis.pipeline.return_value
        pipe.execute.return_value = [None, 10, None, None]
        
        result = await rate_limiter_with_redis.acquire("api_key")
        
        assert result is False
        # Should remove the request we just added
        mock_redis.zrem.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_redis_pipeline_operations(self, rate_limiter_with_redis, mock_redis):
        """Should execute proper Redis pipeline operations"""
        pipe = mock_redis.pipeline.return_value
        pipe.execute.return_value = [None, 0, None, None]
        
        await rate_limiter_with_redis.acquire("test_key", rate=20, period=120)
        
        # Verify pipeline operations
        pipe.zremrangebyscore.assert_called_once()
        pipe.zcard.assert_called_once()
        pipe.zadd.assert_called_once()
        pipe.expire.assert_called_once()
        pipe.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_redis_error_fails_open(self, rate_limiter_with_redis, mock_redis):
        """Should fail open (allow request) on Redis errors"""
        pipe = mock_redis.pipeline.return_value
        pipe.execute.side_effect = Exception("Redis connection error")
        
        # Should not raise, and should allow request
        result = await rate_limiter_with_redis.acquire("test_key")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_redis_key_format(self, rate_limiter_with_redis, mock_redis):
        """Should use correct Redis key format"""
        pipe = mock_redis.pipeline.return_value
        pipe.execute.return_value = [None, 0, None, None]
        
        await rate_limiter_with_redis.acquire("groq_api")
        
        # Check that zremrangebyscore was called with correct key
        call_args = pipe.zremrangebyscore.call_args[0]
        assert call_args[0] == "rate_limit:groq_api"


class TestWaitIfNeeded:
    """Test wait_if_needed method"""
    
    @pytest.mark.asyncio
    async def test_wait_if_needed_waits_when_limited(self):
        """Should wait and retry when rate limited"""
        limiter = RateLimiter(default_rate=1, default_period=1)
        
        # Use up the limit
        await limiter.acquire("test")
        
        # Start timer
        start = time.time()
        
        # This should wait ~1 second for window to expire
        await limiter.wait_if_needed("test")
        
        elapsed = time.time() - start
        
        # Should have waited at least 0.9 seconds
        assert elapsed >= 0.9
    
    @pytest.mark.asyncio
    async def test_wait_if_needed_returns_immediately_when_allowed(self, rate_limiter):
        """Should return immediately when request is allowed"""
        start = time.time()
        
        await rate_limiter.wait_if_needed("test")
        
        elapsed = time.time() - start
        
        # Should be almost instant
        assert elapsed < 0.1
    
    @pytest.mark.asyncio
    async def test_wait_if_needed_custom_params(self):
        """Should respect custom rate and period in wait_if_needed"""
        limiter = RateLimiter()
        
        # Use up custom limit
        for _ in range(5):
            await limiter.acquire("test", rate=5, period=1)
        
        start = time.time()
        
        # Should wait for window
        await limiter.wait_if_needed("test", rate=5, period=1)
        
        elapsed = time.time() - start
        # Should have waited some time (relaxed assertion)
        assert elapsed >= 0.5


class TestConcurrency:
    """Test concurrent rate limiting"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_respect_limit(self):
        """Should properly rate limit concurrent requests"""
        limiter = RateLimiter(default_rate=5, default_period=10)
        
        # Launch 10 concurrent requests
        tasks = [limiter.acquire("concurrent") for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Exactly 5 should succeed
        allowed_count = sum(1 for r in results if r is True)
        assert allowed_count == 5
    
    @pytest.mark.asyncio
    async def test_concurrent_different_keys(self):
        """Should handle concurrent requests to different keys"""
        limiter = RateLimiter(default_rate=2, default_period=10)
        
        # Concurrent requests to different keys
        tasks = [
            limiter.acquire("key1"),
            limiter.acquire("key2"),
            limiter.acquire("key1"),
            limiter.acquire("key2"),
        ]
        results = await asyncio.gather(*tasks)
        
        # All should succeed (each key gets its own bucket)
        assert all(results)


class TestEdgeCases:
    """Test edge cases"""
    
    @pytest.mark.asyncio
    async def test_very_high_rate_allows_all(self, rate_limiter):
        """Should allow all requests with very high rate"""
        limiter = RateLimiter(default_rate=1000000, default_period=60)
        
        # Make 100 requests
        for _ in range(100):
            result = await limiter.acquire("test")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_empty_string_key(self, rate_limiter):
        """Should handle empty string keys"""
        result = await rate_limiter.acquire("", rate=5, period=10)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_unicode_keys(self, rate_limiter):
        """Should handle unicode in keys"""
        result = await rate_limiter.acquire("限制器🚦", rate=5, period=10)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_very_short_period(self, rate_limiter):
        """Should handle very short periods"""
        limiter = RateLimiter(default_rate=2, default_period=0.5)
        
        # Use up limit
        await limiter.acquire("test")
        await limiter.acquire("test")
        
        # Wait for window
        await asyncio.sleep(0.6)
        
        # Should be allowed again
        result = await limiter.acquire("test")
        assert result is True


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_groq_api_rate_limiting(self):
        """Should simulate Groq API rate limiting (10 req/min)"""
        limiter = RateLimiter(default_rate=10, default_period=60)
        
        # Make 10 rapid requests (should all succeed)
        for i in range(10):
            result = await limiter.acquire("groq_api")
            assert result is True, f"Request {i+1} should be allowed"
        
        # 11th request should be rate limited
        result = await limiter.acquire("groq_api")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_multiple_api_keys_independent(self):
        """Should track multiple APIs independently"""
        limiter = RateLimiter(default_rate=3, default_period=10)
        
        # Use up Groq limit
        for _ in range(3):
            await limiter.acquire("groq_api")
        
        # Semrush should still be available
        result = await limiter.acquire("semrush_api")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_burst_then_throttle_pattern(self):
        """Should handle burst then throttle pattern"""
        limiter = RateLimiter(default_rate=5, default_period=2)
        
        # Burst: make 5 requests rapidly
        start = time.time()
        for _ in range(5):
            result = await limiter.acquire("burst_api")
            assert result is True
        burst_time = time.time() - start
        
        # Should complete quickly (< 0.5 seconds)
        assert burst_time < 0.5
        
        # Now rate limited
        assert await limiter.acquire("burst_api") is False
        
        # Wait for window
        await asyncio.sleep(2.1)
        
        # Should be allowed again
        assert await limiter.acquire("burst_api") is True
