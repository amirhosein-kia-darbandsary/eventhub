from fastapi.routing import APIRouter
from app.schemas.event import EventRead
from app.schemas.common import CursorPage
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.event import Event, EventStatus
from app.api.deps import get_current_partner
from app.db.session import get_db
from app.core.pagination import paginate
from fastapi import Depends, Query
from app.models.partener_key import PartnerApiKey

partner_router = APIRouter(prefix="/api/v1/partners", tags=['partners'])


@partner_router.get(path="/events", response_model=CursorPage[EventRead])
async def get_events(db: AsyncSession = Depends(get_db),
                     partner: PartnerApiKey = Depends(get_current_partner),
                     cursor: str | None = Query(default=None),
                     limit: int = Query(default=20, ge=1, le=100)):
    stmt = select(Event).where(Event.status == EventStatus.published)
    events = await db.execute(stmt)
    rows, next_cursor, has_more = await paginate(
        db, stmt, sort_column=Event.starts_at, id_column=Event.id, cursor=cursor, limit=limit
    )

    return CursorPage[EventRead](items=rows, next_cursor=next_cursor, has_more=has_more)
