from pathlib import Path
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.schemas.common import ErrorResponse

_request_log: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleWare(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        recent = [t for t in _request_log[client_ip] if t > window_start]
        _request_log[client_ip] = recent

        if len(recent) >= self.max_requests:
            body = ErrorResponse(
                code="rate_limited",
                message=f"Too many requests. Limit is {self.max_requests} per {self.window_seconds}s.",
                details={"retry_after_seconds": self.window_seconds},
            )
            return JSONResponse(
                status_code=429,
                content=body.model_dump(),
                headers={"Retry-After": str(self.window_seconds)},
            )

        recent.append(now)
        return await call_next(request)


_LUA_SCRIPT_PATH = Path(__file__).parent.parent / "rate_limit.lua"


class RedisRateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, redis_client, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.redis_client = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.script = redis_client.register_script(
            _LUA_SCRIPT_PATH.read_text())

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        allowed = await self.script(keys=[key], args=[self.max_requests, self.window_seconds])

        if not allowed:
            body = ErrorResponse(
                code="rate_limited",
                message=f"Too many requests. Limit is {self.max_requests} per {self.window_seconds}s.",
                details={"retry_after_seconds": self.window_seconds},
            )
            return JSONResponse(
                status_code=429,
                content=body.model_dump(),
                headers={"Retry-After": str(self.window_seconds)},
            )

        return await call_next(request)
