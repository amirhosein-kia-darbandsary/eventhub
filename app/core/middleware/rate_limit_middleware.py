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
