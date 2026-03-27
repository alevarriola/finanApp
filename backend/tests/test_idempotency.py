import uuid

import pytest
from graphql import GraphQLError

from app.core.idempotency import check_idempotency, raise_duplicate, save_idempotency


async def test_check_returns_none_for_new_key():
    user_id = uuid.uuid4()
    key = uuid.uuid4()
    result = await check_idempotency(user_id, key)
    assert result is None


async def test_save_then_check_returns_cached():
    user_id = uuid.uuid4()
    key = uuid.uuid4()
    response = {"id": str(uuid.uuid4()), "status": "created"}

    await save_idempotency(user_id, key, response)
    result = await check_idempotency(user_id, key)

    assert result is not None
    assert result["status"] == "created"


async def test_different_users_different_keys():
    user1 = uuid.uuid4()
    user2 = uuid.uuid4()
    key = uuid.uuid4()  # same key, different users

    await save_idempotency(user1, key, {"user": "1"})

    result1 = await check_idempotency(user1, key)
    result2 = await check_idempotency(user2, key)

    assert result1 is not None
    assert result2 is None


async def test_different_keys_same_user():
    user_id = uuid.uuid4()
    key1 = uuid.uuid4()
    key2 = uuid.uuid4()

    await save_idempotency(user_id, key1, {"key": "1"})

    result1 = await check_idempotency(user_id, key1)
    result2 = await check_idempotency(user_id, key2)

    assert result1 is not None
    assert result2 is None


async def test_raise_duplicate_throws_graphql_error():
    with pytest.raises(GraphQLError) as exc_info:
        raise_duplicate()
    assert "Duplicate request" in str(exc_info.value)
    assert exc_info.value.extensions["statusCode"] == 409
