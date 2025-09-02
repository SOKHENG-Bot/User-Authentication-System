import logging
from datetime import datetime, timezone

from app.models.user_model import User
from app.services.authorization_service import AuthorizationService
from app.services.util_service import UtilService
from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_accounts(self, current_user: dict):
        """Retrieve a list of all user accounts."""
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            accounts_statement = await self.session.execute(select(User))
            accounts = accounts_statement.scalars().all()
            return accounts
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def suspend_account(self, account_id: int, current_user: dict):
        """Suspend a user account."""
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            account_statement = await self.session.execute(
                select(User).where(User.id == account_id)
            )
            account = account_statement.scalars().first()
            account.is_active = False
            await self.session.commit()
            return account
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def unsuspend_account(self, account_id: int, current_user: dict):
        """Unsuspend a previously suspended user account."""
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            account_statement = await self.session.execute(
                select(User).where(User.id == account_id)
            )
            account = account_statement.scalars().first()
            account.is_active = True
            await self.session.commit()
            return account
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def reset_account_password_admin(
        self, account_id: int, new_password: str, current_user: dict
    ):
        """Reset a user's password as an admin."""
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            account_statement = await self.session.execute(
                select(User).where(User.id == account_id)
            )
            account = account_statement.scalars().first()

            account.hash_password = UtilService.hash_password(new_password)
            self.session.add(account)
            await self.session.commit()
            await self.session.refresh(account)
            return account
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def bulk_account_actions(
        self, account_ids: list[int], action: str, current_user: dict
    ):
        """Perform bulk actions on multiple user accounts."""
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            if not account_ids:
                return {"status": "error", "message": "No user IDs provided."}

            try:
                if action == "activate":
                    await self.session.execute(
                        update(User)
                        .where(User.id.in_(account_ids))
                        .values(is_active=True, updated_at=datetime.now(timezone.utc))
                    )
                elif action == "deactivate":
                    await self.session.execute(
                        update(User)
                        .where(User.id.in_(account_ids))
                        .values(is_active=False, updated_at=datetime.now(timezone.utc))
                    )
                elif action == "delete":
                    await self.session.execute(
                        delete(User).where(User.id.in_(account_ids))
                    )
                else:
                    return {
                        "status": "error",
                        "message": f"Unsupported action: {action}",
                    }
                await self.session.commit()
                return {"status": "success", "action": action, "user_ids": account_ids}
            except HTTPException:
                raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err
