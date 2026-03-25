import json
import uuid

import redis.asyncio as aioredis
from graphql import GraphQLError

from app.core.config import get_settings

_TTL_SECONDS = 300  # 5 minutes


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(get_settings().redis_url, decode_responses=True)


def _key(user_id: uuid.UUID, idempotency_key: uuid.UUID) -> str:
    return f"idempotency:{user_id}:{idempotency_key}"


async def check_idempotency(user_id: uuid.UUID, idempotency_key: uuid.UUID) -> dict | None:
    r = await _get_redis()
    try:
        cached = await r.get(_key(user_id, idempotency_key))
        if cached:
            return json.loads(cached)
        return None
    finally:
        await r.aclose()


async def save_idempotency(user_id: uuid.UUID, idempotency_key: uuid.UUID, response: dict) -> None:
    r = await _get_redis()
    try:
        await r.set(_key(user_id, idempotency_key), json.dumps(response), ex=_TTL_SECONDS)
    finally:
        await r.aclose()


def raise_duplicate() -> None:
    raise GraphQLError(
        "Duplicate request — this operation was already processed",
        extensions={"statusCode": 409, "type": "IdempotencyError"},
    )
