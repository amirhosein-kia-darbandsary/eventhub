from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select
from app.models.reserve import Reservation, ReservationStatus
from app.models.ticket_type import TicketType
import uuid
from app.exceptions.common import NotFoundError, ConflictError
from sqlalchemy.exc import IntegrityError
from app.services.ticket_type_service import calculate_available
from datetime import datetime, timedelta, timezone

DEFAULT_TTL_MINUTES = 15


async def create_reservation_service(db: AsyncEngine,
                             ticket_type_id: int,
                             quantity: int,
                             user_id: uuid.UUID,
                             idempotency_key: str | None = None) -> Reservation:
    if idempotency_key is not None:
        existing = db.execute(select(Reservation).where(Reservation.idempotency_key==idempotency_key))
        existing_reservation = existing.scalar_one_or_none()
    
        if existing_reservation is not None:
            return existing_reservation 
    
    result = await db.execute(
        select(TicketType).where(TicketType.id ==
                                 ticket_type_id).with_for_update()
    )
    ticket_type: TicketType = result.scalar_one_or_none()
    if ticket_type is None:
        raise NotFoundError("TicketType", ticket_type_id)

    available = calculate_available(ticket_type.total_quantity,
                                    ticket_type.reserved_quantity,
                                    ticket_type.sold_quantity)
    if quantity > available:
        raise ConflictError(f"Not enough tickets available (requested {quantity},\
                            available {available}")

    ticket_type.reserved_quantity += quantity

    reservation = Reservation(user_id=user_id,
                                 ticket_type_id=ticket_type_id,
                                 quantity=quantity,
                                 idempotency_key=idempotency_key,
                                 status=ReservationStatus.pending,
                                 expires_at=datetime.now(timezone.utc) + timedelta(minutes=DEFAULT_TTL_MINUTES))
    db.add(reservation)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        if idempotency_key is None:
            raise
        existing = await db.execute(
            select(Reservation).where(Reservation.idempotency_key == idempotency_key)
        )
        return existing.scalar_one()

    await db.refresh(reservation)
    return reservation