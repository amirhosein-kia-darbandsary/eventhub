import redis.asyncio as redis

from app.core.config import get_settings

_settings = get_settings()

redis_client = redis.from_url(_settings.redis.url, decode_responses=True)

