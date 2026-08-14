from typing import Callable, Awaitable, Any
from app.core.redis_client_ import redis_client
import json


async def cache_aside(key: str, ttl_seconds: int,
                      compute: Callable[[], Awaitable[Any]]) -> Any:

    cached = await redis_client.get(key)
    if cached is not None:
        return json.loads(cached)

    result = await compute()
    await redis_client.set(key, json.dumps(result), ex=ttl_seconds)
    return result


async def invalidate_cache(*keys: str) -> None:
    if keys:
        await redis_client.delete(*keys)
