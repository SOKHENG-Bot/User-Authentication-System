import logging
from datetime import datetime, timezone

from app.models.user_model import User
from app.schemas.user_schemas import UserUpdateProfile
from app.services.authorization_service import AuthorizationService
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
admin_dependency = Depends(AuthorizationService(session=AsyncSession).check_permissions)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_profile(self, current_user: User):
        """Retrieve the profile of the current logged-in user."""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
            statement = await self.session.execute(
                select(User).where(User.email == current_user["email"])
            )
            user = statement.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Get account profile failed due to server down",
            ) from err

    async def update_user_profile(self, data: UserUpdateProfile, current_user: User):
        """Update the profile of the current logged-in user."""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
            statement = await self.session.execute(
                select(User).where(User.email == current_user["email"])
            )
            account = statement.scalars().first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            # Update user fields
            for var, value in vars(data).items():
                setattr(account, var, value) if value else None
            account.updated_at = datetime.now(timezone.utc)
            self.session.add(account)
            await self.session.commit()
            return account
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Update account failed due to server down",
            ) from err

    async def delete_account(self, account_id: int, current_user: dict):
        """Delete the current logged-in user's account."""
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            statement = await self.session.execute(
                select(User).where(User.id == int(account_id))
            )
            account = statement.scalars().first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            await self.session.delete(account)
            await self.session.commit()
            return {"message": "Account deleted successfully."}
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delete account failed due to server down",
            ) from err

    async def get_user_sessions(self):
        """List all active sessions for the current user."""
        try:
            statement = await self.session.execute(select(User).where(User.is_active))
            accounts = statement.scalars().all()
            if not accounts:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active sessions found",
                )
            return accounts
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Get session failed due to server down",
            ) from err
