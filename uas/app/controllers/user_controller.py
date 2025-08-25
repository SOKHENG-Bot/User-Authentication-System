from app.configuration.database import get_db
from app.schemas.user_schemas import (
    LoginProfile,
    PasswordReset,
    UserLogin,
    UserProfile,
    UserRegister,
)
from app.services.auth_service import AuthService
from app.services.password_service import PasswordService
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter()


@auth_router.post(
    "/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED
)
async def register_account(
    data: UserRegister,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await AuthService(session).register_account(data, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/login", response_model=LoginProfile, status_code=status.HTTP_200_OK)
async def login_account(data: UserLogin, session: AsyncSession = Depends(get_db)):
    try:
        return await AuthService(session).authenticate_account(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# @auth_router.post("/logout", status_code=status.HTTP_200_OK)
# async def logout_account(data: UserLogin, session: AsyncSession = Depends(get_db)):
#    pass

# @auth_router.post("/refresh-token", status_code=status.HTTP_200_OK)
# async def refresh_token():
#    pass


@auth_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await PasswordService(session).reset_password_request(
            email, background_tasks
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    data: PasswordReset,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await PasswordService(session).reset_password(data, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.get(
    "/verify-email/{token}", response_model=UserProfile, status_code=status.HTTP_200_OK
)
async def verify_email(
    token: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await AuthService(session).verify_email_address(token, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.get("/verify-email-password-reset/{token}", status_code=status.HTTP_200_OK)
async def verify_email_password_reset(
    token: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await PasswordService(session).verify_email_address_password_reset(
            token, background_tasks
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await AuthService(session).resend_verification_email(
            email, background_tasks
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password():
    pass


@auth_router.get("/profile", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def get_profile():
    pass


@auth_router.put("/profile", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def update_profile():
    pass


@auth_router.post("/enable-2fa", status_code=status.HTTP_200_OK)
async def enable_2fa():
    pass


@auth_router.post("/verify-2fa", status_code=status.HTTP_200_OK)
async def verify_2fa():
    pass


@auth_router.delete("/account", status_code=status.HTTP_200_OK)
async def delete_account():
    pass


@auth_router.get("/sessions", status_code=status.HTTP_200_OK)
async def list_sessions():
    pass


@auth_router.delete("/sessions/{id}", status_code=status.HTTP_200_OK)
async def revoke_session(id: int):
    pass
