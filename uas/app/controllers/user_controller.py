from app.configuration.database import get_async_session
from app.schemas.user_schemas import (
    LoginProfile,
    PasswordChange,
    PasswordReset,
    UserProfile,
    UserRegister,
    UserUpdateProfile,
)
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.authorization_service import AuthorizationService
from app.services.logging_service import LoggingService
from app.services.password_service import PasswordService
from app.services.session_service import SessionService
from app.services.social_authentication_service import (
    SocialAuthenticationService,
)
from app.services.token_service import TokenService
from app.services.user_service import UserService
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

auth_router = APIRouter()
user_router = APIRouter()
admin_router = APIRouter()

admin_dependency = Depends(AuthorizationService(session=AsyncSession).check_permissions)
user_dependency = Depends(AuthService(session=AsyncSession).get_current_user_via_cookie)
refresh_dependency = Depends(
    AuthService(session=AsyncSession).get_current_user_via_refresh_cookie
)
db_dependency = Depends(get_async_session)


@auth_router.post(
    "/signup",
    response_model=UserProfile,
    status_code=status.HTTP_201_CREATED,
)
async def signup_account(
    data: UserRegister,
    background_tasks: BackgroundTasks,
    session=db_dependency,
):
    """Register a new user account."""
    try:
        return await AuthService(session).sigup_account(data, background_tasks)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.get(
    "/continue-google",
    status_code=status.HTTP_200_OK,
)
async def oauth_google(session=db_dependency):
    """Authenticate a user via social login and return JWT tokens."""
    try:
        return await SocialAuthenticationService(session).oauth_google()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.get(
    "/continue-google/callback",
    status_code=status.HTTP_200_OK,
)
async def oauth_google_callback(
    request: Request,
    response: Response,
    session=db_dependency,
):
    """Handle Google OAuth2 callback and return JWT tokens."""
    try:
        return await SocialAuthenticationService(session).oauth_google_callback(
            request, response
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.post(
    "/signin",
    status_code=status.HTTP_200_OK,
)
async def login_account_cookie(
    response: Response,
    session=db_dependency,
    data: OAuth2PasswordRequestForm = Depends(),
):
    """Authenticate a user and set JWT token in HttpOnly cookie."""
    try:
        return await AuthService(session).login_and_store_cookie(response, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.post(
    "/signout",
    status_code=status.HTTP_200_OK,
)
async def logout_account(
    response: Response,
    session=db_dependency,
    authorize=user_dependency,
):
    """Logout the current user by invalidating their token. This Route Need Cookie Authorization"""
    try:
        return await TokenService(session).revoke_token(authorize, response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.post(
    "/signout-all-device",
    status_code=status.HTTP_200_OK,
)
async def logout_account_all_device(
    response: Response,
    session=db_dependency,
    authorize=user_dependency,
):
    """Logout the current user by invalidating their token. This Route Need Cookie Authorization"""
    try:
        return await TokenService(session).revoke_token_all_device(authorize, response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.post(
    "/refresh-token",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    response: Response,
    session=db_dependency,
    authorize=refresh_dependency,
):
    """Refresh the JWT token for the current user. This Route Need Cookie Authorization"""
    try:
        return await TokenService(session).refresh_access_token(authorize, response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session=db_dependency,
):
    """Initiate the password reset process for a user account."""
    try:
        return await PasswordService(session).reset_password_request(
            email, background_tasks
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    data: PasswordReset,
    background_tasks: BackgroundTasks,
    session=db_dependency,
):
    """Reset the password for a user account."""
    try:
        return await PasswordService(session).reset_password(data, background_tasks)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.get(
    "/verify-email/{token}",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
)
async def email_address_verify(
    token: str,
    background_tasks: BackgroundTasks,
    session=db_dependency,
):
    """Verify a user's email address using the provided token."""
    try:
        return await AuthService(session).email_address_verify(token, background_tasks)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.get(
    "/verify-email-password-reset/{token}",
    status_code=status.HTTP_200_OK,
)
async def verify_email_password_reset(
    token: str,
    background_tasks: BackgroundTasks,
    session=db_dependency,
):
    """Verify a user's email address during password reset using the provided token."""
    try:
        return await PasswordService(session).verify_email_address_password_reset(
            token, background_tasks
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@auth_router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
)
async def email_address_verify_resend(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session=db_dependency,
):
    """Resend the email verification link to the user's email address."""
    try:
        return await AuthService(session).email_address_verify_resend(
            email, background_tasks
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@user_router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    data: PasswordChange,
    session=db_dependency,
    authorize=user_dependency,
):
    """Change the password for a logged-in user. This Route Need Cookie Authorization"""
    try:
        return await PasswordService(session).change_password(
            authorize, data.old_password, data.new_password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@user_router.get(
    "/profile",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    session=db_dependency,
    authorize=user_dependency,
):
    """Get the profile of the current logged-in user. This Route Need Cookie Authorization"""
    try:
        return await UserService(session).get_user_profile(authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@user_router.put(
    "/profile",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    data: UserUpdateProfile,
    session=db_dependency,
    authorize=user_dependency,
):
    """Update the profile of the current logged-in user. This Route Need Cookie Authorization"""
    try:
        return await UserService(session).update_user_profile(data, authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@user_router.get(
    "/sessions",
    response_model=list[LoginProfile],
    status_code=status.HTTP_200_OK,
)
async def list_sessions(session=db_dependency):
    """List all active sessions for the current user. This Route Need Cookie Authorization"""
    try:
        return await UserService(session).get_user_sessions()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.delete(
    "/sessions/{id}",
    status_code=status.HTTP_200_OK,
)
async def revoke_session(
    account_id: int, session=db_dependency, authorize=user_dependency
):
    """Revoke a specific session for the current user. This Route Need Cookie Authorization"""
    try:
        return await SessionService(session).terminate_session(account_id, authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.delete(
    "/account",
    status_code=status.HTTP_200_OK,
)
async def delete_account(
    account_id: int,
    session=db_dependency,
    authorize=user_dependency,
):
    """Delete the current logged-in user's account. This Route Need Cookie Authorization"""
    try:
        return await UserService(session).delete_account(account_id, authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.get("/get-active-session", status_code=status.HTTP_200_OK)
async def get_active_session(
    session=db_dependency,
    authorize=user_dependency,
):
    try:
        return await SessionService(session).get_active_sessions(authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.post("/assign-role", status_code=status.HTTP_200_OK)
async def assign_role(
    account_id: int, new_role: str, session=db_dependency, authorize=user_dependency
):
    """Assing new role to account"""
    try:
        return await AuthorizationService(session).assign_role(
            account_id, new_role, authorize
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.get("/get-all-account", status_code=status.HTTP_200_OK)
async def get_all_account(session=db_dependency, authorize=user_dependency):
    try:
        return await AdminService(session).get_all_accounts(authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.post("/suspend-account", status_code=status.HTTP_200_OK)
async def suspend_account(
    account_id: int, session=db_dependency, authorize=user_dependency
):
    try:
        return await AdminService(session).suspend_account(account_id, authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.post("/unsuspend-account", status_code=status.HTTP_200_OK)
async def unsuspend_account(
    account_id: int, session=db_dependency, authorize=user_dependency
):
    try:
        return await AdminService(session).unsuspend_account(account_id, authorize)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.post("/reset-password-by-admin", status_code=status.HTTP_200_OK)
async def reset_password_by_admin(
    account_id: int, new_password: str, session=db_dependency, authorize=user_dependency
):
    try:
        return await AdminService(session).reset_account_password_admin(
            account_id, new_password, authorize
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.get("/get-account-logs", status_code=status.HTTP_200_OK)
async def get_account_logs(
    account_id: int, session=db_dependency, authorize=user_dependency
):
    try:
        return await LoggingService(session).get_user_activity_logs(
            account_id, authorize
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.get("/get-log-report", status_code=status.HTTP_200_OK)
async def get_log_report(
    account_id: int, session=db_dependency, authorize=user_dependency
):
    try:
        return await LoggingService(session).generate_security_report(
            account_id, authorize
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.post("/bulk-account", status_code=status.HTTP_200_OK)
async def bulk_account(
    account_ids: list[int],
    action: str,
    session=db_dependency,
    authorize=user_dependency,
):
    try:
        return await AdminService(session).bulk_account_actions(
            account_ids, action, authorize
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
