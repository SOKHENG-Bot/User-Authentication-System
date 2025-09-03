import uuid
from datetime import datetime, timedelta, timezone

import jwt
from app.configuration.settings import settings
from app.models.user_model import User, UserSession
from app.services.ad_security_service import AdvancedSecurityService
from fastapi import HTTPException, status
from sqlalchemy import delete, select
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

    async def revoke_token(self, current_user: dict, response: Response):
        account_id = current_user["user_id"]
        account_statement = await self.session.execute(
            select(User).where(User.id == int(account_id))
        )
        account = account_statement.scalars().first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
            )
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)

        await self.session.execute(
            delete(UserSession).where(UserSession.id == int(account_id))
        )
        await self.session.commit()
        # Clear the token cookie
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return {"message": "Successfully signout."}

    async def revoke_token_all_device(self, current_user: dict, response: Response):
        account_id = current_user["user_id"]
        account_statement = await self.session.execute(
            select(User).where(User.id == int(account_id))
        )
        account = account_statement.scalars().first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
            )
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        await self.session.execute(
            delete(UserSession).where(UserSession.user_id == int(account_id))
        )
        await self.session.commit()
        # Clear the token cookie
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return {"message": "Successfully signout."}

    async def get_access_token_from_cookie(self, request: Request):
        """Extract the JWT token from HttpOnly cookies."""
        access_token = request.cookies.get("access_token")
        if not access_token:
            return None
        return access_token

    async def get_refresh_token_from_cookie(self, request: Request):
        """Extract the JWT refresh token from HttpOnly cookies."""
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return None
        return refresh_token

    async def refresh_access_token(self, current_user: dict, response: Response):
        from app.services.session_service import SessionService

        await AdvancedSecurityService(self).check_rate_limit(
            account_email=current_user["email"]
        )
        account_id = current_user["user_id"]
        account_statement = await self.session.execute(
            select(User).where(User.id == int(account_id))
        )
        account = account_statement.scalars().first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid refresh token",
            )
        await SessionService(self.session).validate_session(account_data=account)
        # Generate JWT tokens for the user
        access_token = TokenService(self.session).generate_token(
            data={
                "user_id": str(account.id),
                "email": account.email,
                "username": account.username,
                "role": account.role,
                "jti": str(uuid.uuid4()),
            },
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        # Generate refresh token for refresh access token
        refresh_token = TokenService(self.session).generate_token(
            data={
                "user_id": str(account.id),
                "email": account.email,
                "username": account.username,
                "role": account.role,
                "jti": str(uuid.uuid4()),
            },
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_in=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            # secure=True,  # Uncomment this in production (requires HTTPS)
            samesite="Lax",  # or "None" if frontend/backend are on different ports
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            # secure=True,
            samesite="Lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )
        return {"access_token": access_token, "expire_time": "1-minutes"}
