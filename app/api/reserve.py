from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.reserve import ReservationCreate, ReservationRead
from fastapi import status, Depends, Header
from app.api.deps import  get_current_user
from app.services.reservation_service import create_reservation_service
from app.models.user import User
reserve_router = APIRouter(prefix="/reservations", tags=["reservations"])


@reserve_router.post('', response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
async def create_reservation(payload:ReservationCreate,
                             user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db),
                             idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),):
    result = await create_reservation_service(db=db,
                                              ticket_type_id=payload.ticket_type_id,
                                              idempotency_key=idempotency_key,
                                              quantity=payload.quantity,
                                              user_id=user.id)
    return result
    
