"""FILE: backend/utils/rate_limiter.py  PURPOSE: Tiny in-memory sliding-window rate limiter (per client IP)."""
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, limit, window=60):
        self.limit, self.window, self.hits = limit, window, defaultdict(deque)

    def allow(self, key):
        now, q = time.monotonic(), self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
