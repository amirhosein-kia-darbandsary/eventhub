import asyncio

import dramatiq
from periodiq import cron

from app.core.setup_dramiq import redis_broker  
from app.db.worker_session import worker_async_session_factory 
from app.services.reservation_service import cleanup_expired_reservations


@dramatiq.actor(max_retries=1, periodic=cron("*/5 * * * *"))
def cleanup_expired_reservations_task():

    async def _run_cleanup():
        async with worker_async_session_factory() as session:
            await cleanup_expired_reservations(session)
            
    asyncio.run(_run_cleanup())


    