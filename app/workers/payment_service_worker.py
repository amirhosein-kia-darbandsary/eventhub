import asyncio
import logging

import dramatiq

from app.core.setup_dramiq import redis_broker  # noqa: F401
from app.db.worker_session import worker_async_session_factory
from app.models.webhook import WebHookEvent, WebHookEventStatus
from app.services.webhook_service import process_payment_webhook_logic

logger = logging.getLogger("eventhub.webhooks")


@dramatiq.actor(max_retries=3, min_backoff=1000)
def process_payment_webhook(webhook_event_id: str) -> None:
    asyncio.run(_run(webhook_event_id))


async def _run(webhook_event_id: str) -> None:
    async with worker_async_session_factory() as session:
        try:
            await process_payment_webhook_logic(session, webhook_event_id)
        except Exception:
            logger.exception(
                f"Failed to process webhook event {webhook_event_id}")
            raise


@dramatiq.actor
def mark_webhook_as_dead_letter(webhook_event_id: str) -> None:
    asyncio.run(_mark_dead(webhook_event_id))


async def _mark_dead(webhook_event_id: str) -> None:
    async with worker_async_session_factory() as session:
        event = await session.get(WebHookEvent, webhook_event_id)
        if event is not None:
            event.status = WebHookEventStatus.dead_letter
            await session.commit()
            logger.critical(
                f"Webhook event {webhook_event_id} moved to dead-letter after all retries failed")
