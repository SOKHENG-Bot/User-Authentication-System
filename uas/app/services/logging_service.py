import logging
from datetime import datetime, timezone

from app.models.user_model import UserActivityLog
from app.services.authorization_service import AuthorizationService
from fastapi import HTTPException, status
from fastapi.requests import Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class LoggingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_authentication_event(
        self, account_data: dict, request: Request, action: str
    ):
        try:
            log_statement = await self.session.execute(
                select(UserActivityLog).where(
                    UserActivityLog.user_id == int(account_data.id)
                )
            )
            log_activity = log_statement.scalars().first()
            if not log_activity:
                log_activity = UserActivityLog(
                    user_id=account_data.id,
                    user_email=account_data.email,
                    action=action,
                    ip_address=request.client.host,
                    device_info=request.headers.get("User-Agent"),
                    created_at=datetime.now(timezone.utc),
                    count=1,
                )
                self.session.add(log_activity)
            else:
                log_activity.ip_address = request.client.host  # str
                log_activity.created_at = datetime.now(timezone.utc)  # datetime
                log_activity.count += 1

            # Only need to add once if it’s new
            if not log_activity.log_id:  # optional check if it’s new
                self.session.add(log_activity)

            await self.session.commit()
            await self.session.refresh(log_activity)
            return log_activity

        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def get_user_activity_logs(self, account_id: int, current_user: dict):
        """Retrieve activity logs for a specific user."""
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
                select(UserActivityLog).where(UserActivityLog.user_id == account_id)
            )
            logs = account_statement.scalars().all()
            if not logs:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No logs available.",
                )
            return {"logs": logs}
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err

    async def generate_security_report(self, account_id: int, current_user: dict):
        try:
            permission = await AuthorizationService(self.session).check_permissions(
                current_user
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This operation is allow only Admin",
                )
            logs_statement = await self.session.execute(
                select(
                    UserActivityLog.action,
                    func.sum(UserActivityLog.count).label("Total_count"),
                )
                .where(UserActivityLog.user_id == account_id)
                .group_by(UserActivityLog.action)
            )
            logs = logs_statement.all()  # List of tuples: [(action, count), ...]
            # Convert to dictionary
            reports = {action: count for action, count in logs}
            return {"Logs": reports}
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error during operation: {err!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed due to server down",
            ) from err
