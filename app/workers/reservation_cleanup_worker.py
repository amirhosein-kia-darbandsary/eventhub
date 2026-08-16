import asyncio

import dramatiq
from periodiq import cron

from app.core.setup_dramiq import redis_broker  
from app.db.session import async_session_factory
from app.services.reservation_service import cleanup_expired_reservations


@dramatiq.actor(max_retries=1, periodic=cron("*/5 * * * *"))
def cleanup_expired_reservations_task():

    asyncio.run(_run_cleanup())


    async def _run_cleanup():
        async with async_session_factory() as session:
            await cleanup_expired_reservations(session)