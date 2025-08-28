from datetime import datetime, timezone

from app.models.user_model import User
from app.schemas.user_schemas import UserUpdateProfile
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_profile(self, current_user: User):
        """Retrieve the profile of the current logged-in user."""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        statement = await self.session.execute(
            select(User).where(User.email == current_user["email"])
        )
        user = statement.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def update_user_profile(self, data: UserUpdateProfile, current_user: User):
        """Update the profile of the current logged-in user."""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        statement = await self.session.execute(
            select(User).where(User.email == current_user["email"])
        )
        account = statement.scalars().first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # Update user fields
        for var, value in vars(data).items():
            setattr(account, var, value) if value else None
        account.updated_at = datetime.now(timezone.utc)
        self.session.add(account)
        await self.session.commit()
        return account

    async def delete_account(self, account_id: int):
        """Delete the current logged-in user's account."""
        statement = await self.session.execute(
            select(User).where(User.id == account_id)
        )
        account = statement.scalars().first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self.session.delete(account)
        await self.session.commit()
        return {"message": "Account deleted successfully."}

    async def get_user_sessions(self):
        """List all active sessions for the current user."""
        statement = await self.session.execute(select(User).where(User.is_active))
        accounts = statement.scalars().all()
        if not accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active sessions found"
            )
        return accounts

    async def logout_all_devices(self):
        """Logout from all devices by invalidating all tokens."""
        pass
