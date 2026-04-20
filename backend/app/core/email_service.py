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
        "subject": "Verify your email — Kash",
        "html": f"""
        <div
            style="font-family: -apple-system, sans-serif; max-width: 480px;
                   margin: 0 auto; padding: 40px 20px;"
        >
            <h2 style="color: #004F39; margin-bottom: 8px;">Welcome to Kash</h2>
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


def send_ai_security_alert_email(
    *,
    user_email: str,
    user_id: uuid.UUID,
    prompt: str,
) -> None:
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    resend.Emails.send({
        "from": settings.resend_from_email,
        "to": settings.ai_chat_admin_alert_emails,
        "subject": f"[{settings.app_name}] Suspicious AI prompt blocked",
        "html": f"""
        <div
            style="font-family: -apple-system, sans-serif; max-width: 560px;
                   margin: 0 auto; padding: 32px 20px;"
        >
            <h2 style="color: #7f1d1d; margin-bottom: 12px;">Suspicious AI prompt blocked</h2>
            <p style="color: #333; font-size: 14px; line-height: 1.6; margin: 0 0 12px;">
                Kash blocked a suspicious AI transaction prompt and kept the request
                from reaching the model.
            </p>
            <div
                style="background: #fff7ed; border: 1px solid #fdba74;
                       border-radius: 12px; padding: 16px;"
            >
                <p style="margin: 0 0 8px; font-size: 13px; color: #7c2d12;">
                    <strong>User email:</strong> {user_email}
                </p>
                <p style="margin: 0 0 8px; font-size: 13px; color: #7c2d12;">
                    <strong>User ID:</strong> {user_id}
                </p>
                <p style="margin: 0; font-size: 13px; color: #7c2d12;">
                    <strong>Prompt:</strong> {prompt}
                </p>
            </div>
        </div>
        """,
    })
