"""
CacheManager Utility
Redis-backed caching for intermediate results to reduce costs
"""
import json
import hashlib
from typing import Any, Optional
from datetime import timedelta


class CacheManager:
    """
    Redis-backed cache with TTL support
    Stores intermediate results to reduce redundant API calls and LLM usage
    """
    
    def __init__(self, redis_client=None, default_ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            redis_client: Redis client instance (optional, falls back to in-memory)
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self._local_cache = {}  # In-memory fallback
    
    def _generate_key(self, namespace: str, identifier: str) -> str:
        """
        Generate cache key with namespace
        
        Args:
            namespace: Cache namespace (e.g., 'web_crawl', 'llm_response')
            identifier: Unique identifier (e.g., URL, prompt hash)
            
        Returns:
            Formatted cache key
        """
        # Hash identifier if it's too long
        if len(identifier) > 100:
            identifier = hashlib.sha256(identifier.encode()).hexdigest()
        
        return f"cache:{namespace}:{identifier}"
    
    async def get(self, namespace: str, identifier: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            
        Returns:
            Cached value or None if not found/expired
        """
        key = self._generate_key(namespace, identifier)
        
        if self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"[CacheManager] Redis get error: {e}")
        else:
            # In-memory fallback
            if key in self._local_cache:
                entry = self._local_cache[key]
                import time
                if time.time() < entry['expires_at']:
                    return entry['value']
                else:
                    del self._local_cache[key]
        
        return None
    
    async def set(self, namespace: str, identifier: str, value: Any, ttl: Optional[int] = None):
        """
        Store value in cache with TTL
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            value: Value to cache (must be JSON-serializable)
            ttl: Time-to-live in seconds (uses default if None)
        """
        key = self._generate_key(namespace, identifier)
        ttl = ttl or self.default_ttl
        
        try:
            serialized = json.dumps(value)
        except (TypeError, ValueError) as e:
            print(f"[CacheManager] Value not JSON-serializable: {e}")
            return
        
        if self.redis:
            try:
                await self.redis.setex(key, ttl, serialized)
            except Exception as e:
                print(f"[CacheManager] Redis set error: {e}")
        else:
            # In-memory fallback
            import time
            self._local_cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
    
    async def delete(self, namespace: str, identifier: str):
        """
        Delete value from cache
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
        """
        key = self._generate_key(namespace, identifier)
        
        if self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                print(f"[CacheManager] Redis delete error: {e}")
        else:
            self._local_cache.pop(key, None)
    
    async def exists(self, namespace: str, identifier: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            
        Returns:
            True if key exists and not expired
        """
        result = await self.get(namespace, identifier)
        return result is not None
    
    async def clear_namespace(self, namespace: str):
        """
        Clear all keys in a namespace
        
        Args:
            namespace: Cache namespace to clear
        """
        if self.redis:
            try:
                pattern = f"cache:{namespace}:*"
                cursor = 0
                while True:
                    cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self.redis.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                print(f"[CacheManager] Redis clear error: {e}")
        else:
            # In-memory fallback
            prefix = f"cache:{namespace}:"
            keys_to_delete = [k for k in self._local_cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._local_cache[key]
    
    async def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats
        """
        if self.redis:
            try:
                info = await self.redis.info('stats')
                return {
                    'backend': 'redis',
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                    'hit_rate': info.get('keyspace_hits', 0) / 
                               max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0))
                }
            except Exception:
                return {'backend': 'redis', 'error': 'stats unavailable'}
        else:
            return {
                'backend': 'in-memory',
                'keys': len(self._local_cache)
            }
    
    def create_cache_key_from_dict(self, data: dict) -> str:
        """
        Generate consistent cache key from dictionary
        Useful for caching function results based on parameters
        
        Args:
            data: Dictionary to hash
            
        Returns:
            Hash string
        """
        # Sort keys for consistency
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
