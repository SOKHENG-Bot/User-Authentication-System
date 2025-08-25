from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from sqlalchemy.future import select
from fastapi import BackgroundTasks

from app.models.user_model import User
from app.schemas.user_schemas import PasswordReset
from app.configuration.settings import settings
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.services.util_service import UtilService

class PasswordService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def reset_password_request(self, email: EmailStr, background_tasks: BackgroundTasks):
        statement = await self.session.execute(select(User).where(User.email == email))
        account = statement.scalars().first()
        if not account:
            raise ValueError("No account found with the provided email.")
        
        token = TokenService().generate_secure_token(
            payload={"user_id": account.id, "email": account.email, "username": account.username},
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_in=300
        )
        await EmailService().send_verification_email_password_reset(account, token, background_tasks)
        return {"message": "Request successful. Please check your email for reset instructions."}

    async def verify_email_address_password_reset(self, token: str, background_tasks: BackgroundTasks):
        payload = TokenService().validate_secure_token(
            token=token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        account_email = payload.get("email")
        if not account_email:
            raise ValueError("Invalid token payload.")
        
        statement = await self.session.execute(select(User).where(User.email == account_email))
        account = statement.scalars().first()
        await EmailService().send_password_reset_email(account, token, background_tasks)
        return {"message": "Token verify successful. You can now reset your password."}

    async def reset_password(self, data: PasswordReset, background_tasks: BackgroundTasks):
        if data.new_password != data.confirm_password:
            raise ValueError("New password and confirm password do not match.")
        hashed_password = UtilService().hash_password(data.new_password)
        statement = await self.session.execute(select(User).where(User.email == data.email))
        account = statement.scalars().first()
        if not account:
            raise ValueError("No account found with the provided email.")
        account.password_hash = hashed_password
        self.session.add(account)
        await self.session.commit()
        await EmailService().send_confirmation_verification_email(account, background_tasks)
        return {"message": "Password reset successful. You can now log in with your new password."}

    def change_password(self):
        pass

    def validate_password_strength(self):
        pass