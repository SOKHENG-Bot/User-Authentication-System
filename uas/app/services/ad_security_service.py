import logging

import httpx
from app.configuration.settings import settings
from fastapi import HTTPException, status
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class AdvancedSecurityService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.max_request = 5
        self.window_seconds = 600  # 15 mins
        self.redis = Redis(host="localhost", port="6379")

    async def check_rate_limit(self, account_email: str):
        """Check and enforce rate limiting on authentication attempts."""
        try:
            key = f"request_attempts by: {account_email}"
            attempts = await self.redis.incr(key)

            if attempts == 1:
                await self.redis.expire(key, self.window_seconds)

            if attempts > self.max_request:
                ttl = await self.redis.ttl(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Try again in {ttl} seconds.",
                )
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def implement_captcha_verification(self, captcha_token: str):
        """Implement CAPTCHA verification for suspicious login attempts."""
        try:
            url = "https://www.google.com/recaptcha/api/siteverify"
            data = {
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "token": captcha_token,
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data)
                result = await response.json()

            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CAPTCHA verification failed.",
                )
            return True  # CAPTCHA passed
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err
