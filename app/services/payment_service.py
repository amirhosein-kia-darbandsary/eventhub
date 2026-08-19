import logging

import httpx
import pybreaker
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings

logger = logging.getLogger("eventhub.payment")

_settings = get_settings()


payment_breaker = pybreaker.CircuitBreaker(fail_max=3,
                                           reset_timeout=15,
                                           name="payment_provider")


class PaymentProviderError(Exception):
    ...


@payment_breaker
@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    reraise=True,
)
def _call_payment_provider(reservation_id: int, amount_cents: int, callback_url: str) -> dict:
    with httpx.Client(timeout=5) as client:
        print(_settings.payment.url)
        response = client.post(
            f"{_settings.payment.url}/payments",
            json={
                "reservation_id": reservation_id,
                "amount_cents": amount_cents,
                "callback_url": callback_url,
            },
        )
        response.raise_for_status()
        return response.json()


async def initiate_payment(reservation_id: int, amount_cents: int, callback_url: str) -> dict:
    from starlette.concurrency import run_in_threadpool

    try:
        return await run_in_threadpool(
            _call_payment_provider, reservation_id, amount_cents, callback_url
        )
    except pybreaker.CircuitBreakerError as e:
        logger.error(f"Payment provider circuit breaker is OPEN: {e}")
        raise PaymentProviderError(
            "Payment provider is temporarily unavailable") from e
    except httpx.HTTPError as e:
        logger.error(f"Payment provider call failed after retries: {e}")
        raise PaymentProviderError("Payment provider request failed") from e
