from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from fastapi import BackgroundTasks
from pydantic import EmailStr

from app.models.user_model import User
from app.services.util_service import UtilService
from app.services.token_service import TokenService
from app.schemas.user_schemas import UserRegister, UserLogin
from app.services.email_service import EmailService
from app.configuration.settings import settings

class AuthService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_account(self, data: UserRegister, background_tasks: BackgroundTasks) -> User:
        existing_account = await self.session.execute(
            select(User).where((User.email == data.email) | (User.username == data.username))
        )
        if existing_account.scalars().first():
            raise ValueError("Email or username already in use.")

        password_hashed = UtilService().hash_password(data.password)
        new_account = User(
            email=data.email,
            username=data.username,
            password_hash=password_hashed,
            role="user",
            is_active=False,
            is_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.session.add(new_account)
        await self.session.commit()
        await self.session.refresh(new_account)

        token = TokenService().generate_secure_token(
            payload={"user_id": new_account.id, "email": new_account.email, "username": new_account.username},
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_in=300
        )
        await EmailService().send_verification_email(new_account, token, background_tasks)
        return new_account
    
    async def verify_email_address(self, token: str, background_tasks: BackgroundTasks):
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
        account.is_verified = True
        account.is_active = True
        account.updated_at = datetime.now(timezone.utc)

        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        await EmailService().send_confirmation_verification_email(account, background_tasks)
        return account


    async def resend_verification_email(self, email: EmailStr, background_tasks: BackgroundTasks):
        statement = await self.session.execute(select(User).where(User.email == email))
        account = statement.scalars().first()
        if not account:
            raise ValueError("Account with this email does not exist.")
        if account.is_verified:
            raise ValueError("Email already verified.")
        
        token = TokenService().generate_secure_token(
            payload={"user_id": account.id, "email": account.email, "username": account.username},
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_in=300
        )
        await EmailService().send_verification_email(account, token, background_tasks)
        return account

    async def authenticate_account(self, data: UserLogin) -> User:
        statement = await self.session.execute(select(User).where(User.email == data.email))
        account = statement.scalars().first()
        if not account:
            raise ValueError("Invalid email or password.")
        
        if not UtilService().verify_password(data.password, account.password_hash):
            raise ValueError("Invalid email or password.")
        
        if not account.is_active or not account.is_verified:
            raise ValueError("Account is not active or email is not verified.")
        
        account.last_login = datetime.now(timezone.utc)
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def login_with_social_account(self):
        pass

    async def logout_account(self):
        pass