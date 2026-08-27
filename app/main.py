from fastapi import FastAPI, Depends
from app.api.deps import require_role

from app.core.config import Settings, get_settings
from app.api.auth import auth_router
from app.api.venue import venue_router
from app.api.event import event_router
from app.api.ticket import ticket_router
from app.api.reserve import reserve_router
from app.api.checkout import checkout_router
from app.api.webhook import webhook_router
from app.core.middleware.request_id_middleware import RequestIDMiddleware
from app.core.middleware.timing_middleware import TimingMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware.rate_limit_middleware import RateLimitMiddleWare
from app.core.error_handlers import register_exception_handlers
# from app.core.setup_dramiq import dramatiq


import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")


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

    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(venue_router)
    app.include_router(event_router)
    app.include_router(ticket_router)
    app.include_router(reserve_router)
    app.include_router(checkout_router)
    app.include_router(webhook_router)

    # RequestID  →  Timing  →  CORS  →  RateLimit  →  GZip  →  Routers
    # Don't Forget boy :) startlet make these things in the reveser :)
    # so you need to add them as reverse .

    # inner middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    # app.add_middleware(RateLimitMiddleWare,
    #                    max_requests=100, window_seconds=60)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)


    @app.get("/healthz")
    def healthz():
        """
        TODO: In here we will add db and redis connection liveness/connections to be correct
        """
        return {"status": "ok"}

    return app


app = create_app()
