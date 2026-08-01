from fastapi import FastAPI, Depends
from app.api.deps import require_role

from app.core.config import Settings, get_settings
from app.api.auth import auth_router
from app.api.venue import venue_router
from app.api.event import event_router
from app.api.ticket import ticket_router

from app.core.error_handlers import register_exception_handlers


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

    @app.get("/admin/ping")
    def admin_ping(user=Depends(require_role("admin"))):
        return {"message": f"hello admin {user.email}"}

    @app.get("/healthz")
    def healthz():
        """
        TODO: In here we will add db and redis connection liveness/connections to be correct
        """
        return {"status": "ok"}

    return app


app = create_app()
