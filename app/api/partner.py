from fastapi.routing import APIRouter
from app.schemas.event import EventRead
from app.schemas.common import CursorPage
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.event import Event, EventStatus
from app.api.deps import get_current_partner, get_current_user, require_role
from app.db.session import get_db
from app.core.pagination import paginate
from fastapi import Depends, Query
from app.models.partener_key import PartnerApiKey
from app.models.user import User
from app.exceptions.common import NotFoundError

from schemas.parnter import *
from app.core.security import generate_api_key, hash_api_key
partner_router = APIRouter(prefix="/api/v1/partners", tags=['partners'])


@partner_router.get(path="/events", response_model=CursorPage[EventRead])
async def get_events(db: AsyncSession = Depends(get_db),
                     partner: PartnerApiKey = Depends(get_current_partner),
                     cursor: str | None = Query(default=None),
                     limit: int = Query(default=20, ge=1, le=100)):
    stmt = select(Event).where(Event.status == EventStatus.published)
    rows, next_cursor, has_more = await paginate(
        db, stmt, sort_column=Event.starts_at, id_column=Event.id, cursor=cursor, limit=limit
    )

    return CursorPage[EventRead](items=rows, next_cursor=next_cursor, has_more=has_more)


@partner_router.post(path="/create-api-key", response_model=ReadPartenerApiKey)
async def create_partner_keys(
    request: CreateParnerApikey, db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    main_api_key = generate_api_key()
    hashed_api_key = hash_api_key(main_api_key)

    partner_api_key = PartnerApiKey(
        partner_name=request.partner_name, hashed_key=hashed_api_key)

    db.add(partner_api_key)

    await db.commit()
    await db.refresh(partner_api_key) 

    return main_api_key


@partner_router.post(path="/update-api-key/{partner_id}", response_model=ReadPartenerApiKey)
async def update_partner_keys(
    partner_id: uuid.UUID,
    request: UpdatePartnerApi,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):

    stmt = select(PartnerApiKey).where(PartnerApiKey.id == partner_id)
    res = await db.execute(stmt)
    partner = res.scalar_one_or_none()
    if partner is None:
        raise NotFoundError("PartnerApiKey", partner_id)
    updates = request.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(partner, field, value)

    await db.commit()
    await db.flush(partner)
    return partner


@partner_router.get(path="/list-api-key", response_model=CursorPage[ReadPartenerApiKey])
async def list_partner_key(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100)
):
    stmt = select(PartnerApiKey)
    rows, next_cursor, has_more = await paginate(
        db, stmt, sort_column=PartnerApiKey.created_at, id_column=PartnerApiKey.id, cursor=cursor, limit=limit
    )

    return CursorPage[PartnerApiKey](items=rows, next_cursor=next_cursor, has_more=has_more)

