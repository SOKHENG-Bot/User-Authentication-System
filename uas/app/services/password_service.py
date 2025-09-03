import logging
import uuid

from app.configuration.settings import settings
from app.models.user_model import User
from app.schemas.user_schemas import PasswordReset
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.services.util_service import UtilService
from fastapi import BackgroundTasks, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = logging.getLogger(__name__)


class PasswordService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def reset_password_request(
        self,
        email: EmailStr,
        background_tasks: BackgroundTasks,
    ) -> dict:
        """Initiate a password reset request by generating a token and sending an email."""
        try:
            statement = await self.session.execute(
                select(User).where(User.email == email)
            )
            account = statement.scalars().first()
            if not account:
                logger.warning(
                    f"Password reset requested for unregistered email: {email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="If the email is registered, you will receive password reset instructions.",
                )
            verification_token = TokenService().generate_token(
                data={
                    "user_id": account.id,
                    "email": account.email,
                    "username": account.username,
                    "jti": str(uuid.uuid4()),  # Unique identifier for the token
                },
                secret_key=settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM,
                expires_in=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            )
            await self.session.commit()
            await EmailService().send_verification_email_password_reset(
                account, verification_token, background_tasks
            )
            return {
                "message": "Request successful. Please check your email for reset instructions."
            }
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during password reset request: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing the password reset request.",
            ) from err

    async def verify_email_address_password_reset(
        self,
        token: str,
        background_tasks: BackgroundTasks,
    ) -> dict:
        """Verify the password reset token and send a confirmation email."""
        try:
            payload = TokenService().validate_token(
                token=token,
                secret_key=settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            account_email = payload.get("email")
            if not account_email:
                logger.warning("Token payload missing email.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token payload.",
                )
            statement = await self.session.execute(
                select(User).where(User.email == account_email)
            )
            account = statement.scalars().first()
            if not account:
                logger.warning(
                    f"Password reset token used for non-existent email: {account_email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No account found with the provided email.",
                )
            await EmailService().send_password_reset_email(
                account, token, background_tasks
            )
            return {
                "message": "Token verify successful. You can now reset your password."
            }
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during password reset token verification: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token verification failed.",
            ) from err

    async def reset_password(
        self,
        data: PasswordReset,
        background_tasks: BackgroundTasks,
    ) -> User:
        """Reset the password for a user account."""
        try:
            if data.new_password != data.confirm_password:
                logger.warning("New password and confirm password do not match.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password and confirm password do not match.",
                )
            statement = await self.session.execute(
                select(User).where(User.email == data.email)
            )
            account = statement.scalars().first()
            if not account:
                logger.warning(
                    f"Password reset attempted for non-existent email: {data.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No account found with the provided email.",
                )
            hashed_password = UtilService().hash_password(data.new_password)
            account.password_hash = hashed_password
            await self.session.commit()
            await self.session.refresh(account)
            await EmailService().send_confirmation_verification_email(
                account, background_tasks
            )
            return account
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during password reset: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while resetting the password.",
            ) from err

    async def change_password(
        self, authorize: dict, old_password: str, new_password: str
    ):
        """Change the password for a logged-in user."""
        try:
            statement = await self.session.execute(
                select(User).where(User.email == authorize.get("email"))
            )
            account = statement.scalars().first()
            if not account:
                logger.warning(
                    f"Password change attempted for non-existent email: {authorize.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No account found with the provided email.",
                )
            if not UtilService().verify_password(old_password, account.password_hash):
                logger.warning("Old password does not match.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old password is incorrect.",
                )
            hashed_password = UtilService().hash_password(new_password)
            account.password_hash = hashed_password
            await self.session.commit()
            await self.session.refresh(account)
            return {"message": "Password changed successfully."}
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during password change: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while changing the password.",
            ) from err
