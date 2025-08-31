import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User

logger = logging.getLogger(__name__)


class AuthorizationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_permissions(
        self,
        account_data: dict,
    ):
        """Check if a user has the required permissions for an action."""
        account_role = account_data["role"]
        if account_role != "admin":
            return False
        return True

    async def assign_role(self, account_id: int, new_role: str, current_user: dict):
        """Assign a role to a user."""
        permission = await self.check_permissions(current_user)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This operation is allow only Admin",
            )
        statement = await self.session.execute(select(User).where(User.id == account_id))
        account = statement.scalars().first()
        if not account:
            return None
        account.role = new_role
        self.session.add(account)
        await self.session.commit()
        return {"Message": f"Account with email {account.email} now assigned to {new_role} "}

    def create_custom_permission(self):
        """Create a custom permission for a user or role."""
        pass
