from app.core.redis_client_ import redis_client
from app.core.cache import invalidate_cache
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.exceptions.common import NotFoundError, ValidationAppError
from app.core.pagination import paginate
from app.db.session import get_db
from app.models.event import Event, EventStatus
from app.schemas.common import CursorPage
from app.schemas.event import EventCreate, EventRead, EventUpdate

from app.repositories.venue_repository import SqlAlchemyVenueRepository
from app.services.event_service import validate_venue_exists
from app.core.cache import cache_aside
event_router = APIRouter(prefix="/events", tags=["events"])


@event_router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    venue_repo = SqlAlchemyVenueRepository(db)
    await validate_venue_exists(payload.venue_id, venue_repo)

    event = Event(**payload.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@event_router.get("", response_model=CursorPage[EventRead])
async def list_events(
    db: AsyncSession = Depends(get_db),
    cursor: str | None = Query(
        default=None, description="مقدار next_cursor از پاسخ قبلی"),
    limit: int = Query(default=20, ge=1, le=100),
    status: EventStatus = Query(default=EventStatus.published)
):
    cache_key = f"events:list:cursor={cursor}:limit={limit}"

    async def fetch_from_db():
        stmt = select(Event).where(Event.status == status)

        try:
            rows, next_cursor, has_more = await paginate(
                db, stmt, sort_column=Event.starts_at, id_column=Event.id, cursor=cursor, limit=limit
            )
        except ValueError:
            raise ValidationAppError("Invalid cursor value")
        page = CursorPage[EventRead](
            items=rows, next_cursor=next_cursor, has_more=has_more)
        return page.model_dump(mode="json")
    return await cache_aside(key=cache_key, ttl_seconds=30, compute=fetch_from_db)


@event_router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    async def fetch_from_db():
        event = await db.get(Event, event_id)
        if event is None:
            raise NotFoundError("Event", event_id)
        return EventRead.model_validate(event).model_dump(mode='json')
    return await cache_aside(f"event:{event_id}", 60, fetch_from_db)


@event_router.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: int,
    payload: EventUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    event = await db.get(Event, event_id)
    if event is None:
        raise NotFoundError("Event", event_id)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(event, field, value)

    if event.ends_at <= event.starts_at:
        raise ValidationAppError("ends_at must be after starts_at")

    await db.commit()
    await db.refresh(event)


    await invalidate_cache(redis_client, f"event:{event_id}")

    return event
