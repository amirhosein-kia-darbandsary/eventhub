import logging

logger = logging.getLogger("eventhub.notifications")


def send_confirmation_email(user_email: str, reservation_id: int) -> None:
    print(f"[DEBUG] send_confirmation_email CALLED with {user_email}, {reservation_id}")  # ← موقت
    logger.info(f"[MOCK EMAIL] Confirmation sent to {user_email} for reservation {reservation_id}")