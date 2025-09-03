from datetime import datetime, timedelta

from app.models.user_model import User
from app.services.authorization_service import AuthorizationService
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SecurityService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_failed_login_attempts(self, account: dict):
        """
        Increment failed login attempts in DB.
        Lock account if attempts exceed threshold.
        """
        account.failed_login_attempts += 1
        await self.session.commit()

        if account.failed_login_attempts >= 5:
            await self.lock_account(account)

    async def lock_account(self, account: dict):
        """Lock a user account after multiple failed login attempts."""
        account.locked_until = datetime.utcnow() + timedelta(
            minutes=15
        )  # 15-minute lock
        await self.session.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked due to multiple failed login attempts. Try again later.",
        )
        return account

    async def unlock_account(self, account_id: int, current_user: dict):
        """Unlock a previously locked user account."""
        permission = await AuthorizationService(self.session).check_permissions(
            current_user
        )
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This operation is allow only Admin",
            )
        statement = await self.session.execute(
            select(User).where(User.id == account_id)
        )
        account = statement.scalars().first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account locked due to multiple failed login attempts. Try again later.",
            )
        account.locked_until = datetime.utcnow()
        await self.session.commit()
        return account
