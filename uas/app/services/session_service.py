import logging
import uuid
from datetime import datetime, timedelta, timezone

from app.configuration.settings import settings
from app.models.user_model import User, UserSession
from app.services.authorization_service import AuthorizationService
from app.services.token_service import TokenService
from fastapi import HTTPException, Request, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(
        self,
        account_data: dict,
        request: Request,
    ):
        """Create a new session for a user."""
        try:
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
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def validate_session(self, account_data: dict):
        """Validate an existing user session. Use this for more secure with authorization with session token in database"""
        try:
            statement = await self.session.execute(
                select(UserSession).where(UserSession.user_id == int(account_data.id))
            )
            account_session = statement.scalars().first()
            if not account_session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid session token.",
                )
            if account_session.expires_at < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired. Please login again.",
                )
            return account_session
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def extend_session(self, account_id: int, extended_day: int):
        """Extend the duration of an active session."""
        try:
            new_expires_at = datetime.now(timezone.utc) + timedelta(days=extended_day)
            await self.session.execute(
                update(UserSession)
                .where(UserSession.user_id == account_id)
                .values(expires_at=new_expires_at)
            )
            await self.session.commit()
            return {
                "account_id": account_id,
                "new_expiry": new_expires_at,
            }
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def terminate_session(self, account_id: int):
        """Terminate an active user session. only single device"""
        try:
            await self.session.execute(
                delete(UserSession).where(UserSession.id == account_id)
            )
            await self.session.commit()
            return {
                "Message": f"You have terminated account session from account ID: {account_id}"
            }
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def get_active_sessions(self, current_user: dict):
        """Retrieve all active sessions for a user. for all device"""
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            account_statement = await self.session.execute(
                select(User).where(User.is_active)
            )
            account = account_statement.scalars().first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Do not have account active",
                )
            session_statement = await self.session.execute(
                select(UserSession).where(UserSession.user_id == int(account.id))
            )
            session_account = session_statement.scalars().first()
            return {"active_sessions": {session_account}}
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err
