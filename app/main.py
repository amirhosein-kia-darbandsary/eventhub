from app.core.logging_info import configure_logging
from app.api.partner import partner_router
from app.core.redis_client_ import redis_client
from app.core.error_handlers import register_exception_handlers
from app.core.middleware.rate_limit_middleware import RedisRateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.middleware.timing_middleware import TimingMiddleware
from app.core.middleware.request_id_middleware import RequestIDMiddleware
from app.api.webhook import webhook_router
from app.api.checkout import checkout_router
from app.api.reserve import reserve_router
from app.api.ticket import ticket_router
from app.api.event import event_router
from app.api.venue import venue_router
from app.api.auth import auth_router
from app.core.config import Settings, get_settings
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from fastapi import FastAPI
from app.core.middleware.metrics_middelware import MetricsMiddleware
import structlog
from app.core.tracing_config import configure_tracing

configure_logging(json_logs=not get_settings().debug)
log = structlog.get_logger()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Use settings as parameters can help use to use the mock settings and prevent
       Using Global state for the Settings 
       as simple : You can inject deffrent settings without change the code, have 
       diffrent state of your app.
    """
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )
    configure_tracing(app)
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(venue_router)
    app.include_router(event_router)
    app.include_router(ticket_router)
    app.include_router(reserve_router)
    app.include_router(checkout_router)
    app.include_router(webhook_router)
    app.include_router(partner_router)

    # RequestID  →  Timing  →  CORS  →  RateLimit  →  GZip  →  Routers
    # Don't Forget boy :) startlet make these things in the reveser :)
    # so you need to add them as reverse .
    # inner middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RedisRateLimitMiddleware,
                       redis_client=redis_client,
                       max_requests=10, window_seconds=60)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/healthz")
    def healthz():
        log.info("healthz_checked")
        """
        TODO: In here we will add db and redis connection liveness/connections to be correct
        """
        return {"status": "ok"}

    return app


app = create_app()
