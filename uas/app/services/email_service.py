from app.configuration.fastmail import send_email
from app.configuration.settings import settings
from app.models.user_model import User
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession


class EmailService:
    def __inti__(self, session: AsyncSession):
        self.session = session

    async def send_verification_email(
        self, data: User, token: str, background_tasks=BackgroundTasks
    ) -> None:
        """Send verification email to the user."""
        message_data = {
            "System_name": "User Authentication System",
            "email": data.email,
            "username": data.username,
            "verification_link": f"{settings.FRONTEND_URL}/auth/verify-email/{token}",
        }
        await send_email(
            subject="Verify Your Email Address",
            recipients=[data.email],
            template_file="email_verification.html",
            context=message_data,
            background_tasks=background_tasks,
        )

    async def send_confirmation_verification_email(
        self, data: User, background_tasks=BackgroundTasks
    ) -> None:
        """Send confirmation email after successful verification."""
        message_data = {
            "System_name": "User Authentication System",
            "email": data.email,
            "username": data.username,
            "login_link": f"{settings.FRONTEND_URL}/auth/login",
        }
        await send_email(
            subject="Email Address Verified Successfully",
            recipients=[data.email],
            template_file="email_verification_confirmation.html",
            context=message_data,
            background_tasks=background_tasks,
        )

    async def send_verification_email_password_reset(
        self, data: User, token: str, background_tasks=BackgroundTasks
    ) -> None:
        """Send verification email for password reset."""
        message_data = {
            "System_name": "User Authentication System",
            "email": data.email,
            "username": data.username,
            "verification_link": f"{settings.FRONTEND_URL}/auth/verify-email-password-reset/{token}",
        }
        await send_email(
            subject="Verify Your Email Address",
            recipients=[data.email],
            template_file="email_verification.html",
            context=message_data,
            background_tasks=background_tasks,
        )

    async def send_password_reset_email(
        self, data: User, token: str, background_tasks=BackgroundTasks
    ) -> None:
        """Send password reset email to the user."""
        message_data = {
            "System_name": "User Authentication System",
            "email": data.email,
            "username": data.username,
            "reset_password_link": f"{settings.FRONTEND_URL}/auth/reset-password",
        }
        await send_email(
            subject="Password Reset Request",
            recipients=[data.email],
            template_file="password_reset.html",
            context=message_data,
            background_tasks=background_tasks,
        )

    async def send_email_confirmation_password_reset(
        self, data: User, background_tasks=BackgroundTasks
    ) -> None:
        """Send confirmation email after successful password reset."""
        message_data = {
            "System_name": "User Authentication System",
            "email": data.email,
            "username": data.username,
            "login_link": f"{settings.FRONTEND_URL}/auth/login",
        }
        await send_email(
            subject="Password Changed Successfully",
            recipients=[data.email],
            template_file="password_change_confirmation.html",
            context=message_data,
            background_tasks=background_tasks,
        )

    def send_security_alert_email(self):
        pass
