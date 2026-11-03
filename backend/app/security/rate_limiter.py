import time
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status, Response
from app.core.config import settings


class SlidingWindowRateLimiter:
    """
    In-memory Sliding Window Rate Limiter.
    Tracks requests per key (IP or User ID) within a rolling window (default 3600s = 1 hour).
    Ready for replacement with Redis sorted sets in distributed environments.
    """
    def __init__(self):
        # Map: key -> list of float timestamps
        self._history: Dict[str, List[float]] = defaultdict(list)
        self.window_seconds: int = 3600

    def _clean_old_requests(self, key: str, current_time: float) -> None:
        threshold = current_time - self.window_seconds
        # Filter timestamps older than threshold
        valid_ts = [ts for ts in self._history[key] if ts > threshold]
        if valid_ts:
            self._history[key] = valid_ts
        else:
            self._history.pop(key, None)

    def is_allowed(self, key: str, max_limit: int) -> Tuple[bool, int, int, int]:
        """
        Evaluates rate limit for a key.
        Returns: (allowed, remaining, limit, reset_in_seconds)
        """
        now = time.time()
        self._clean_old_requests(key, now)

        timestamps = self._history[key]
        current_count = len(timestamps)

        if current_count >= max_limit:
            # Earliest timestamp determines reset time
            oldest_ts = timestamps[0]
            reset_in = max(1, int(oldest_ts + self.window_seconds - now))
            return False, 0, max_limit, reset_in

        # Add current timestamp
        timestamps.append(now)
        remaining = max(0, max_limit - len(timestamps))
        reset_in = self.window_seconds
        return True, remaining, max_limit, reset_in

    def clear(self):
        """Reset limiter state (useful for tests)."""
        self._history.clear()


limiter = SlidingWindowRateLimiter()


def get_client_ip(request: Request) -> str:
    """
    Safely resolves client IP address considering proxy headers like X-Forwarded-For.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # First IP in X-Forwarded-For is client origin
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


async def check_rate_limit(
    request: Request,
    response: Response,
    tier_override: Optional[str] = None
) -> None:
    """
    FastAPI dependency that enforces rate limits and sets security response headers.
    
    Limits:
    - Anonymous: 10 / hour per client IP
    - Registered: 100 / hour per user
    - Premium: 10,000 / hour per user
    """
    # 1. Determine Identity & Tier
    user_claims = getattr(request.state, "user", None)
    
    if user_claims and "sub" in user_claims:
        user_id = user_claims["sub"]
        tier = tier_override or user_claims.get("tier", "registered")
        key = f"user:{user_id}"
        
        if tier == "premium" or tier == "admin":
            limit = settings.RATE_LIMIT_PREMIUM_PER_HOUR
        else:
            limit = settings.RATE_LIMIT_REGISTERED_PER_HOUR
    else:
        ip = get_client_ip(request)
        key = f"ip:{ip}"
        limit = settings.RATE_LIMIT_ANONYMOUS_PER_HOUR

    allowed, remaining, max_limit, reset_seconds = limiter.is_allowed(key, limit)

    # Attach standard RateLimit headers to response
    response.headers["X-RateLimit-Limit"] = str(max_limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_seconds)

    if not allowed:
        response.headers["Retry-After"] = str(reset_seconds)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Maximum of {max_limit} requests per hour allowed for your tier.",
                "retry_after_seconds": reset_seconds
            },
            headers={
                "Retry-After": str(reset_seconds),
                "X-RateLimit-Limit": str(max_limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_seconds)
            }
        )

