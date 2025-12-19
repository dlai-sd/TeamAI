"""
Rate limiting middleware for FastAPI
Prevents abuse and ensures fair usage
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import time

class RateLimiter:
    """
    Simple in-memory rate limiter
    Production: Use Redis for distributed rate limiting
    """
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
    
    def _clean_old_requests(self, requests: list, window_seconds: int):
        """Remove requests outside the time window"""
        cutoff = time.time() - window_seconds
        return [req_time for req_time in requests if req_time > cutoff]
    
    def check_rate_limit(self, client_id: str) -> Tuple[bool, str]:
        """
        Check if client has exceeded rate limits
        Returns: (is_allowed, error_message)
        """
        current_time = time.time()
        
        # Clean old requests
        self.minute_requests[client_id] = self._clean_old_requests(
            self.minute_requests[client_id], 60
        )
        self.hour_requests[client_id] = self._clean_old_requests(
            self.hour_requests[client_id], 3600
        )
        
        # Check limits
        if len(self.minute_requests[client_id]) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        
        if len(self.hour_requests[client_id]) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
        
        # Record request
        self.minute_requests[client_id].append(current_time)
        self.hour_requests[client_id].append(current_time)
        
        return True, ""
    
    def get_rate_limit_headers(self, client_id: str) -> dict:
        """Return rate limit info for response headers"""
        minute_remaining = self.requests_per_minute - len(self.minute_requests[client_id])
        hour_remaining = self.requests_per_hour - len(self.hour_requests[client_id])
        
        return {
            "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
            "X-RateLimit-Remaining-Minute": str(max(0, minute_remaining)),
            "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
            "X-RateLimit-Remaining-Hour": str(max(0, hour_remaining))
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting
    Uses IP address as client identifier
    """
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Get client identifier (IP address)
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    is_allowed, error_message = rate_limiter.check_rate_limit(client_ip)
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": error_message,
                "retry_after": "60 seconds"
            },
            headers={"Retry-After": "60"}
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    headers = rate_limiter.get_rate_limit_headers(client_ip)
    for key, value in headers.items():
        response.headers[key] = value
    
    return response
