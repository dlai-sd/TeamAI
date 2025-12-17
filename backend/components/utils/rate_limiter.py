"""
RateLimiter Utility
Redis-backed rate limiting to prevent API throttling
"""
import asyncio
import time
from typing import Optional
from datetime import datetime, timedelta


class RateLimiter:
    """
    Token bucket rate limiter with Redis backend
    Prevents API throttling for external services (Groq, Semrush, etc.)
    """
    
    def __init__(self, redis_client=None, default_rate: int = 10, default_period: int = 60):
        """
        Initialize rate limiter
        
        Args:
            redis_client: Redis client instance (optional, falls back to in-memory)
            default_rate: Default number of requests allowed
            default_period: Period in seconds
        """
        self.redis = redis_client
        self.default_rate = default_rate
        self.default_period = default_period
        self._local_buckets = {}  # In-memory fallback
    
    async def acquire(self, key: str, rate: Optional[int] = None, period: Optional[int] = None) -> bool:
        """
        Acquire rate limit token
        
        Args:
            key: Rate limit key (e.g., 'groq_api', 'semrush_api')
            rate: Requests allowed (uses default if None)
            period: Period in seconds (uses default if None)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        rate = rate or self.default_rate
        period = period or self.default_period
        
        if self.redis:
            return await self._acquire_redis(key, rate, period)
        else:
            return await self._acquire_local(key, rate, period)
    
    async def wait_if_needed(self, key: str, rate: Optional[int] = None, period: Optional[int] = None):
        """
        Wait until rate limit allows request
        
        Args:
            key: Rate limit key
            rate: Requests allowed
            period: Period in seconds
        """
        while not await self.acquire(key, rate, period):
            await asyncio.sleep(0.1)  # Wait 100ms and retry
    
    async def _acquire_redis(self, key: str, rate: int, period: int) -> bool:
        """Redis-backed token bucket implementation"""
        redis_key = f"rate_limit:{key}"
        current_time = int(time.time())
        window_start = current_time - period
        
        try:
            # Use Redis sorted set for sliding window
            pipe = self.redis.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(redis_key, 0, window_start)
            
            # Count current window requests
            pipe.zcard(redis_key)
            
            # Add current request
            pipe.zadd(redis_key, {str(current_time): current_time})
            
            # Set expiry
            pipe.expire(redis_key, period + 1)
            
            results = await pipe.execute()
            current_count = results[1]
            
            # Allow if under rate limit
            if current_count < rate:
                return True
            else:
                # Rate limited - remove the request we just added
                await self.redis.zrem(redis_key, str(current_time))
                return False
        
        except Exception as e:
            print(f"[RateLimiter] Redis error: {e}, falling back to allow")
            return True  # Fail open
    
    async def _acquire_local(self, key: str, rate: int, period: int) -> bool:
        """In-memory token bucket implementation (fallback)"""
        current_time = time.time()
        
        if key not in self._local_buckets:
            self._local_buckets[key] = {
                'tokens': rate,
                'last_update': current_time,
                'rate': rate,
                'period': period
            }
        
        bucket = self._local_buckets[key]
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - bucket['last_update']
        tokens_to_add = (time_elapsed / period) * rate
        bucket['tokens'] = min(rate, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = current_time
        
        # Try to consume a token
        if bucket['tokens'] >= 1.0:
            bucket['tokens'] -= 1.0
            return True
        else:
            return False
    
    async def get_remaining(self, key: str, rate: Optional[int] = None, period: Optional[int] = None) -> int:
        """
        Get remaining requests in current window
        
        Args:
            key: Rate limit key
            rate: Requests allowed
            period: Period in seconds
            
        Returns:
            Number of remaining requests
        """
        rate = rate or self.default_rate
        period = period or self.default_period
        
        if self.redis:
            redis_key = f"rate_limit:{key}"
            current_time = int(time.time())
            window_start = current_time - period
            
            try:
                # Remove old entries and count
                pipe = self.redis.pipeline()
                pipe.zremrangebyscore(redis_key, 0, window_start)
                pipe.zcard(redis_key)
                results = await pipe.execute()
                current_count = results[1]
                
                return max(0, rate - current_count)
            except Exception:
                return rate  # Assume full capacity on error
        else:
            bucket = self._local_buckets.get(key)
            if bucket:
                return int(bucket['tokens'])
            return rate
    
    async def reset(self, key: str):
        """Reset rate limit for a key (useful for testing)"""
        if self.redis:
            redis_key = f"rate_limit:{key}"
            await self.redis.delete(redis_key)
        else:
            self._local_buckets.pop(key, None)
