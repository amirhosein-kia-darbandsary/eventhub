from app.core.setup_dramiq import redis_broker
import logging

import dramatiq
logger = logging.getLogger("eventhub.notifications")


@dramatiq.actor(max_retries=3, min_backoff=10000)
def send_confirmation_email(user_email: str, reservation_id: int) -> None:
    logger.info(
        f"[MOCK EMAIL] Confirmation sent to {user_email} for reservation {reservation_id}")
