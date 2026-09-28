import redis.asyncio as redis

from app.core.config import get_settings
import asyncio
_settings = get_settings()

redis_client = redis.from_url(_settings.redis.url, decode_responses=True)

async def _ping():
    print(await redis_client.ping())


async def run():
    await _ping()

if __name__ == "__main__":
    asyncio.run(run())
