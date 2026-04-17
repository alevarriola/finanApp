import redis.asyncio as aioredis


async def consume_rate_limit(
    redis_url: str,
    key: str,
    limit: int,
    window_seconds: int,
) -> bool:
    redis = aioredis.from_url(redis_url, decode_responses=True)
    try:
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window_seconds)
        return current <= limit
    finally:
        await redis.aclose()
