import logging
import uuid
from datetime import datetime, timedelta, timezone

from app.configuration.settings import settings
from app.models.user_model import User, UserSession
from app.schemas.user_schemas import UserRegister
from app.services.email_service import EmailService
from app.services.security_service import SecurityService
from app.services.session_service import SessionService
from app.services.token_service import TokenService
from app.services.util_service import UtilService
from fastapi import BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_current_user_via_cookie(
        self,
        token: str = Depends(
            TokenService(session=AsyncSession).get_access_token_from_cookie
        ),
    ) -> dict:
        """Protected route using HttpOnly cookie for authentication."""
        try:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            payload = TokenService(self.session).validate_token(
                token=token,
                secret_key=settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error retrieving user via cookie: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
            ) from err

    async def get_current_user_via_refresh_cookie(
        self,
        token: str = Depends(
            TokenService(session=AsyncSession).get_refresh_token_from_cookie
        ),
    ) -> dict:
        """Protected route using HttpOnly cookie for authentication."""
        try:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            payload = TokenService(self.session).validate_token(
                token=token,
                secret_key=settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error retrieving user via cookie: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
            ) from err

    async def sigup_account(
        self, data: UserRegister, background_tasks: BackgroundTasks
    ) -> User:
        """Register a new user account and send a verification email."""
        try:
            existing_account = await self.session.execute(
                select(User).where(
                    (User.email == data.email) | (User.username == data.username)
                )
            )
            if existing_account.scalars().first():
                logging.warning("Attempt to register with existing email or username.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email or username already in use.",
                )
            password_hashed = UtilService().hash_password(data.password)
            new_account = User(
                email=data.email,
                username=data.username,
                password_hash=password_hashed,
                role="user",
                is_active=False,
                is_verified=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.session.add(new_account)
            await self.session.commit()
            await self.session.refresh(new_account)
            verifification_token = TokenService(self.session).generate_token(
                data={
                    "user_id": str(new_account.id),
                    "email": new_account.email,
                    "username": new_account.username,
                    "jti": str(uuid.uuid4()),
                },
                secret_key=settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM,
                expires_in=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            )
            await EmailService().send_verification_email(
                new_account, verifification_token, background_tasks
            )
            return new_account

        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account registration failed.",
            ) from err

    async def email_address_verify(
        self, token: str, background_tasks: BackgroundTasks
    ) -> User:
        """Verify a user's email address using the provided token."""
        try:
            payload = TokenService(self.session).validate_token(
                token=token,
                secret_key=settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            account_email = payload.get("email")
            if not account_email:
                logger.warning("Token payload does not contain email.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token payload.",
                )
            statement = await self.session.execute(
                select(User).where(User.email == account_email)
            )
            account = statement.scalars().first()
            account.is_verified = True
            account.is_active = True
            account.updated_at = datetime.now(timezone.utc)

            self.session.add(account)
            await self.session.commit()
            await self.session.refresh(account)
            await EmailService().send_confirmation_verification_email(
                account, background_tasks
            )
            return account
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification failed.",
            ) from err

    async def email_address_verify_resend(
        self,
        email: EmailStr,
        background_tasks: BackgroundTasks,
    ) -> User:
        """Resend the email verification link to the user's email address."""
        try:
            statement = await self.session.execute(
                select(User).where(User.email == email)
            )
            account = statement.scalars().first()
            if not account:
                logger.warning(
                    f"Resend verification requested for non-existent email: {email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No account found with the provided email.",
                )
            if account.is_verified:
                logger.info(f"Email already verified for account: {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already verified.",
                )
            verifification_token = TokenService(self.session).generate_token(
                data={
                    "user_id": str(account.id),
                    "email": account.email,
                    "username": account.username,
                    "jti": str(uuid.uuid4()),
                },
                secret_key=settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM,
                expires_in=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            )
            await EmailService().send_verification_email(
                account, verifification_token, background_tasks
            )
            return account
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resend verification email.",
            ) from err

    async def authenticate_account(
        self,
        data: OAuth2PasswordRequestForm = Depends(),
    ) -> User:
        """Authenticate a user and return access and access tokens."""
        try:
            statement = await self.session.execute(
                select(User).where(User.email == data.username)
            )
            account = statement.scalars().first()
            if not account:
                logger.warning(f"Login attempt with invalid email: {data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email or password.",
                )
            if not UtilService().verify_password(data.password, account.password_hash):
                logger.warning(f"Invalid password attempt for email: {data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email or password.",
                )
            if not account.is_active or not account.is_verified:
                logger.warning(
                    f"Inactive or unverified account login attempt: {data.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive or email not verified.",
                )
            account.last_login = datetime.now(timezone.utc)
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
            refresh_token = TokenService(self.session).generate_token(
                data={
                    "user_id": str(account.id),
                    "email": account.email,
                    "username": account.username,
                    "jti": str(uuid.uuid4()),
                },
                secret_key=settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM,
                expires_in=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            )
            user_session = UserSession(
                user_id=account.id,
                session_token=refresh_token,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc)
                + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            )
            self.session.add(user_session)
            self.session.add(account)
            await self.session.commit()
            await self.session.refresh(account)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
            }
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed due to server error.",
            ) from err

    async def login_and_store_cookie(
        self,
        response: Response,
        request: Request,
        data: OAuth2PasswordRequestForm = Depends(),
    ):
        """Authenticate a user and store JWT tokens in HttpOnly cookies."""
        try:
            statement = await self.session.execute(
                select(User).where(User.email == data.username)
            )
            account = statement.scalars().first()

            if account.locked_until <= datetime.utcnow():
                account.failed_login_attempts = 0
                await self.session.commit()

            if not account:
                await SecurityService(self.session).record_failed_login_attempts(
                    account
                )
                logger.warning(f"Login attempt with invalid email: {data.username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email or password.",
                )
            # Verify password
            if not UtilService().verify_password(data.password, account.password_hash):
                await SecurityService(self.session).record_failed_login_attempts(
                    account
                )
                logger.warning(f"Invalid password attempt for email: {data.username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email or password.",
                )
            # Check status
            if not account.is_active or not account.is_verified:
                logger.warning(
                    f"Inactive/unverified account login attempt: {data.username}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive or email not verified.",
                )
            # Update last login
            account.last_login = datetime.now(timezone.utc)
            self.session.add(account)
            await self.session.commit()
            await self.session.refresh(account)
            # Generate access and refresh tokens cookiea
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
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
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
            # Store tokens in HttpOnly cookies
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                # secure=True,
                samesite="Lax",
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
            account.failed_login_attempts = 0
            await self.session.commit()
            return {
                "message": "Login successful",
                "access_token_cookie": {"token": access_token},
                "refresh_token_cookie": {"token": refresh_token},
                "token_type": "Bearer",
            }
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed due to server error.",
            ) from err
