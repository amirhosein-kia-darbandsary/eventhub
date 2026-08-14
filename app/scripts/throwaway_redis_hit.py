from app.core.config import get_settings
import json
import redis.asyncio as redis
import asyncio

CACHE_TTL_SECONDS = 30
settings = get_settings()
redis_client = redis.from_url(settings.redis.url)
import time

async def expensive_computation(x: int) -> dict:
    await asyncio.sleep(0.2)
    return {"x": x, "result": x * x}


async def get_cached_or_compute(x: int) -> dict:
    cache_key = f"demo:computation:{x}"

    cached = await redis_client.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    result = await expensive_computation(x)
    await redis_client.set(cache_key, json.dumps(result), ex=CACHE_TTL_SECONDS)
    return result


async def main():
 
    start = time.perf_counter()
    result1 = await get_cached_or_compute(7)
    miss_time = (time.perf_counter() - start) * 1000
    print(f"اولین درخواست (cache miss): {miss_time:.1f}ms -> {result1}")
 
    start = time.perf_counter()
    result2 = await get_cached_or_compute(7)
    hit_time = (time.perf_counter() - start) * 1000
    print(f"دومین درخواست (cache hit):  {hit_time:.1f}ms -> {result2}")
 
    print(f"\nنسبت سرعت: cache hit تقریباً {miss_time / hit_time:.0f} برابر سریع‌تر بود")
 
 
asyncio.run(main())
