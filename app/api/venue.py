from fastapi import APIRouter, status, Depends, Query
from app.schemas.venue import *
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_role
from app.models.venue import Venue
from app.exceptions.common import NotFoundError
from sqlalchemy import Select

venue_router = APIRouter(prefix='/venue', tags=['venues'])


@venue_router.post('', response_model=VenueRead, status_code=status.HTTP_201_CREATED)
async def create_venue(payload: VenueCreate,
                       db: AsyncSession = Depends(get_db),
                       admin=Depends(require_role('admin'))):
    venue = Venue(**payload.model_dump())
    db.add(venue)
    await db.commit()
    await db.refresh(venue)

    return venue


@venue_router.get("/{venue_id}", response_model=VenueRead)
async def get_venue(venue_id: int, db: AsyncSession = Depends(get_db)):
    venue = await db.get(Venue, venue_id)
    if venue is None:
        raise NotFoundError("Venue", venue_id)
    return venue


@venue_router.patch("/{venue_id}", response_model=VenueRead)
async def update_venue(
    venue_id: int,
    payload: VenueUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    venue = await db.get(Venue, venue_id)
    if venue is None:
        raise NotFoundError("Venue", venue_id)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(venue, field, value)

    await db.commit()
    await db.refresh(venue)
    return venue


@venue_router.get("", response_model=list[VenueRead])
async def list_venues(db: AsyncSession = Depends(get_db), limit: int = Query(default=10,
                                                                             ge=1,
                                                                             lt=100)):
    stm = Select(Venue).order_by(Venue.id.asc()).limit(limit)
    result = await db.execute(stm)
    return list(result.scalars().all())
