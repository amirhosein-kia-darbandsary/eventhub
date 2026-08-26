from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Depends
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.models.reserve import Reservation, ReservationStatus
from app.models.ticket_type import TicketType
from sqlalchemy import select
from app.exceptions.common import NotFoundError
from app.exceptions.common import ConflictError
from app.services.payment_service import initiate_payment, PaymentProviderError
from fastapi import Path
from app.core.config import INT32_MAX

checkout_router = APIRouter(prefix="/checkout", tags=['checkout'])


@checkout_router.post('/{reservation_id}', status_code=status.HTTP_200_OK)
async def checkout_api(
    reservation_id: int = Path(gt=0, lt=INT32_MAX),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reservation = await db.get(Reservation, reservation_id)
    if reservation is None or reservation.user_id != user.id:
        raise NotFoundError("Reservation", reservation_id)

    if reservation.status != ReservationStatus.pending:
        raise ConflictError(
            f"Cannot pay for a reservation with status '{reservation.status.value}'")

    ticket_type = await db.get(TicketType, reservation.ticket_type_id)
    amount_cents = ticket_type.price_cents * reservation.quantity

    callback_url = "http://localhost:8000/webhooks/payment"
    try:
        payment_result = await initiate_payment(reservation.id, amount_cents, callback_url)
    except PaymentProviderError as e:
        raise ConflictError(str(e))

    return {
        "status": "payment_initiated",
        "reservation_id": reservation.id,
        "payment_id": payment_result["payment_id"],
    }
