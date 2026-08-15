from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Depends
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.models.reserve import Reservation
from sqlalchemy import select
from app.exceptions.common import NotFoundError
from fastapi.background import BackgroundTasks
from app.services.reservation_service import confirm_reservation
from app.services.notification_service import  send_confirmation_email

checkout_router = APIRouter(prefix="/checkout", tags=['checkout'])


@checkout_router.post('/{reservation_id}', status_code=status.HTTP_200_OK)
async def checkout_api(reservation_id:int,
                       background_tasks: BackgroundTasks,
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(get_current_user)):
    reservation = await confirm_reservation(db, reservation_id, user.id)

    background_tasks.add_task(send_confirmation_email, user.email, reservation.id)

    return {"status": "confirmed", "reservation_id": reservation.id}
