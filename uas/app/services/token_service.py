from datetime import datetime, timedelta, timezone

import jwt
from app.models.user_model import UserSession
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response


class TokenService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def generate_token(
        self, data: dict, secret_key: str, algorithm: str, expires_in: int
    ) -> str:
        """Generate a JWT token."""
        payload = data.copy()
        payload.update(
            {"exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in)}
        )
        token = jwt.encode(data, secret_key, algorithm=algorithm)
        return token

    def validate_token(self, token: str, secret_key: str, algorithms: list) -> dict:
        """Validate a JWT token and return the payload."""
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload

    def refresh_token(self):
        pass

    async def revoke_token(
        self, user_id: int, response: Response, all_sessions: bool = False
    ):
        """
        Revoke token for user:
        - If all_sessions is True, revoke all tokens for the user.
        - If all_sessions is False, revoke only the current session's token.
        """
        if all_sessions:
            # Logic to revoke all tokens for the user
            await self.session.execute(
                delete(UserSession).where(UserSession.user_id == user_id)
            )
        else:
            # Logic to revoke only the current session's token
            # This requires identifying the current session, which might involve
            # extracting a token from the request context or similar.
            pass

        await self.session.commit()
        # Clear the token cookie
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return {"message": "Successfully logged out."}

    def blacklist_token(self):
        pass

    async def get_token_from_cookie(self, request: Request):
        """Extract the JWT token from HttpOnly cookies."""
        token = request.cookies.get("access_token")
        if not token:
            return None
        return token
