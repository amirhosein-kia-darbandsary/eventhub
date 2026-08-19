from starlette.concurrency import run_in_threadpool
from app.workers.notification_worker import send_confirmation_email
from app.models.user import User
import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import WebHookEvent, WebHookEventStatus
from app.services.reservation_service import confirm_reservation_internal

logger = logging.getLogger("eventhub.webhooks")


async def process_payment_webhook_logic(db: AsyncSession, webhook_event_id: str) -> None:
    logger.debug(webhook_event_id)
    event = await db.get(WebHookEvent, webhook_event_id)
    if event is None:
        return
    logger.debug(event)
    payload = json.loads(event.payload)
    logger.debug(payload)
    if payload.get("status") == "succeeded":
        reservation_id = payload["reservation_id"]
        reservation = await confirm_reservation_internal(db, reservation_id)

        user = await db.get(User, reservation.user_id)
        await run_in_threadpool(send_confirmation_email.send, user.email, reservation.id)

    event.status = WebHookEventStatus.processed
    await db.commit()
