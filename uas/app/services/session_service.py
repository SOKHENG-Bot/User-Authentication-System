import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.settings import settings
from app.models.user_model import UserSession
from app.services.token_service import TokenService


class SessionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(
        self,
        account_data: dict,
        request: Request,
    ):
        """Create a new session for a user."""
        session_token = TokenService(self.session).generate_token(
            data={
                "user_id": str(account_data.id),
                "email": account_data.email,
                "username": account_data.username,
                "role": account_data.role,
                "jti": str(uuid.uuid4()),
            },
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_in=settings.SESSION_TOKEN_EXPIRE_MINUTES,
        )
        token_statement = await self.session.execute(
            select(UserSession).where(UserSession.user_id == account_data.id)
        )
        user_session = token_statement.scalars().first()
        if not user_session:
            user_session = UserSession(
                user_id=account_data.id,
                session_token=session_token,
                device_info=request.headers.get("User-Agent"),
                ip_address=request.client.host,
                expires_at=datetime.now(timezone.utc)
                + timedelta(settings.SESSION_TOKEN_EXPIRE_MINUTES),
                created_at=datetime.now(timezone.utc),
            )
            self.session.add(user_session)
        else:
            user_session.session_token = session_token
            user_session.device_info = request.headers.get("User-Agent")
            user_session.ip_address = request.client.host
            user_session.expires_at = datetime.now(timezone.utc) + timedelta(
                settings.SESSION_TOKEN_EXPIRE_MINUTES
            )
            self.session.add(user_session)
        await self.session.commit()
        await self.session.refresh(user_session)
        return user_session

    def validate_session(self):
        """Validate an existing user session."""
        pass

    def extend_session(self):
        """Extend the duration of an active session."""
        pass

    def terminate_session(self):
        """Terminate an active user session."""
        pass

    def get_active_sessions(self):
        """Retrieve all active sessions for a user."""
        pass
