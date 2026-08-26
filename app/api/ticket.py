from app.core.config import INT32_MAX
from fastapi import Path
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.exceptions.common import NotFoundError
from app.db.session import get_db
from app.models.ticket_type import TicketType
from app.schemas.ticket import TicketTypeCreate, TicketTypeRead

ticket_router = APIRouter(prefix="/ticket-types", tags=["ticket-types"])


@ticket_router.post("", response_model=TicketTypeRead, status_code=status.HTTP_201_CREATED)
async def create_ticket_type(
    payload: TicketTypeCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    ticket_type = TicketType(**payload.model_dump())
    db.add(ticket_type)
    await db.commit()
    await db.refresh(ticket_type)
    return ticket_type


@ticket_router.get("/{ticket_type_id}", response_model=TicketTypeRead)
async def get_ticket_type(ticket_type_id: int = Path(gt=0, lt=INT32_MAX), db: AsyncSession = Depends(get_db)):
    ticket_type = await db.get(TicketType, ticket_type_id)
    if ticket_type is None:
        raise NotFoundError("TicketType", ticket_type_id)
    return ticket_type
