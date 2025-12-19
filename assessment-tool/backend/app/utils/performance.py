"""
Performance monitoring utilities
Track API response times, database query performance, etc.
"""
import time
from functools import wraps
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
import statistics


class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.call_counts: Dict[str, int] = defaultdict(int)
    
    def record_metric(self, name: str, duration: float):
        """Record a performance metric"""
        self.metrics[name].append(duration)
        self.call_counts[name] += 1
    
    def get_stats(self, name: str = None) -> Dict:
        """Get statistics for a metric or all metrics"""
        if name:
            if name not in self.metrics:
                return {"error": f"Metric {name} not found"}
            
            durations = self.metrics[name]
            return {
                "name": name,
                "calls": self.call_counts[name],
                "min": min(durations),
                "max": max(durations),
                "mean": statistics.mean(durations),
                "median": statistics.median(durations),
                "p95": statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else max(durations),
                "p99": statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else max(durations)
            }
        else:
            return {
                metric_name: self.get_stats(metric_name)
                for metric_name in self.metrics.keys()
            }
    
    def reset(self, name: str = None):
        """Reset metrics"""
        if name:
            self.metrics[name].clear()
            self.call_counts[name] = 0
        else:
            self.metrics.clear()
            self.call_counts.clear()


# Global monitor instance
monitor = PerformanceMonitor()


def track_performance(name: str = None):
    """Decorator to track function performance"""
    def decorator(func):
        metric_name = name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = (time.time() - start) * 1000  # Convert to ms
                monitor.record_metric(metric_name, duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (time.time() - start) * 1000  # Convert to ms
                monitor.record_metric(metric_name, duration)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class TimerContext:
    """Context manager for timing code blocks"""
    
    def __init__(self, name: str):
        self.name = name
        self.start = None
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        duration = (time.time() - self.start) * 1000
        monitor.record_metric(self.name, duration)


# Convenience function
def timer(name: str):
    """Create a timer context manager"""
    return TimerContext(name)
