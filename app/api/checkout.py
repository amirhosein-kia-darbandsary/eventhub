from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Depends
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.models.reserve import Reservation
from sqlalchemy import select
from app.exceptions.common import NotFoundError
from app.services.reservation_service import confirm_reservation
from app.workers.notification_worker import send_confirmation_email
from starlette.concurrency import run_in_threadpool
from redis.exceptions import RedisError
from app.services.reservation_service import logger
checkout_router = APIRouter(prefix="/checkout", tags=['checkout'])


@checkout_router.post('/{reservation_id}', status_code=status.HTTP_200_OK)
async def checkout_api(reservation_id: int,
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(get_current_user)):

    reservation = await confirm_reservation(db, reservation_id, user.id)

    try:
        await run_in_threadpool(send_confirmation_email.send, user.email, reservation.id)
    except RedisError:
        logger.error(
            f"Failed to enqueue confirmation email for reservation {reservation.id}", exc_info=True)

    return {"status": "confirmed", "reservation_id": reservation.id}
