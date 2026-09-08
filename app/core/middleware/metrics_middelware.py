import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.metrics import http_request_duration_seconds


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        route = request.scope.get("route")
        path = route.path if route else request.url.path

        http_request_duration_seconds.labels(
            method=request.method, path=path, status_code=response.status_code
        ).observe(elapsed)

        return response