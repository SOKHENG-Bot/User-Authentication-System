import uuid
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.requests import Request
from starlette.responses import Response

from app.configuration.settings import settings
from app.models.user_model import User
from app.services.session_service import SessionService
from app.services.token_service import TokenService
from app.services.util_service import UtilService


class SocialAuthenticationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def oauth_google(self) -> RedirectResponse:
        """Redirect the user to Google's OAuth2 consent screen."""
        # Construct the Google OAuth2 authorization URL
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&scope=email%20profile"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        return {"Location": google_auth_url}

    async def oauth_google_callback(self, request: Request, response: Response):
        """Handle Google OAuth2 callback and return JWT tokens."""
        # Extract the authorization code from the request
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided.",
            )
        # Exchange the authorization code for an access token
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        # Use httpx to make async HTTP requests
        async with httpx.AsyncClient() as client:
            google_response = await client.post(
                "https://oauth2.googleapis.com/token", data=data, timeout=10
            )
            if google_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to obtain access token from Google.",
                )
            google_token = google_response.json()
            google_access_token = google_token.get("access_token")
            if not google_access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Access token not found in Google's response.",
                )
            # Retrieve user info from Google
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                params={"access_token": google_access_token},
            )
            if user_info_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to obtain user info from Google.",
                )
            user_info = user_info_response.json()
            # Process user info and create or retrieve user account
            email = user_info.get("email")
            username = user_info.get("name") or email.split("@")[0]
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not found in Google's user info.",
                )
            # Check if the user already exists
            statement = await self.session.execute(
                select(User).where(User.email == email)
            )
            account = statement.scalars().first()
            # If not, create a new user account
            if not account:
                account = User(
                    email=email,
                    username=username,
                    password_hash=UtilService().hash_password(uuid.uuid4().hex),
                    role="user",
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                self.session.add(account)
                await self.session.commit()
                await self.session.refresh(account)
            # Update last login time
            if account:
                account.last_login = datetime.now(timezone.utc)
                self.session.add(account)
                await self.session.commit()
                await self.session.refresh(account)
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
            await SessionService(self.session).create_session(
                account_data=account, request=request
            )
            # Redirect to frontend with tokens in HttpOnly cookies
            swagger_ui_url = "/docs"
            redirect = RedirectResponse(url=swagger_ui_url)
            # Set the access token in an HttpOnly cookie
            redirect.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                # secure=True,  # Uncomment this in production (requires HTTPS)
                samesite="Lax",  # or "None" if frontend/backend are on different ports
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )
            redirect.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                # secure=True,
                samesite="Lax",
                max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            )
            return redirect

    def link_social_account(self):
        """Link a social account to the current user."""
        pass

    def unlink_social_account(self):
        """Unlink a social account from the current user."""
        pass

    def get_social_accounts(self):
        """Get linked social accounts for the current user."""
        pass
