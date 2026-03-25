import json
import uuid

import redis.asyncio as aioredis
import resend

from app.core.config import get_settings

_VERIFY_TTL = 86400  # 24 hours


def _key(token: uuid.UUID) -> str:
    return f"email_verify:{token}"


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(get_settings().redis_url, decode_responses=True)


async def create_verification_token(user_id: uuid.UUID, email: str) -> uuid.UUID:
    token = uuid.uuid4()
    r = await _get_redis()
    try:
        await r.set(
            _key(token),
            json.dumps({"user_id": str(user_id), "email": email}),
            ex=_VERIFY_TTL,
        )
    finally:
        await r.aclose()
    return token


async def get_verification_data(token: uuid.UUID) -> dict | None:
    r = await _get_redis()
    try:
        data = await r.get(_key(token))
        if data:
            await r.delete(_key(token))
            return json.loads(data)
        return None
    finally:
        await r.aclose()


def send_verification_email(to_email: str, token: uuid.UUID) -> None:
    settings = get_settings()
    resend.api_key = settings.resend_api_key
    verify_url = f"{settings.frontend_url}/verify-email?token={token}"

    resend.Emails.send({
        "from": settings.resend_from_email,
        "to": [to_email],
        "subject": "Verify your email — FinanApp",
        "html": f"""
        <div style="font-family: -apple-system, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;">
            <h2 style="color: #004F39; margin-bottom: 8px;">Welcome to FinanApp</h2>
            <p style="color: #333; font-size: 15px; line-height: 1.6;">
                Click the button below to verify your email address.
            </p>
            <a href="{verify_url}"
               style="display: inline-block; background-color: #004F39; color: #FFFACA;
                      padding: 12px 28px; border-radius: 8px; text-decoration: none;
                      font-weight: 600; font-size: 14px; margin: 20px 0;">
                Verify email
            </a>
            <p style="color: #999; font-size: 12px; margin-top: 24px;">
                This link expires in 24 hours. If you didn't create an account, ignore this email.
            </p>
        </div>
        """,
    })
