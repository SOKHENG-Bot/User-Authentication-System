from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

    # Custom validator to restrict certain email domains
    @field_validator("email")
    def validate_email(cls, validate: str) -> str:
        if validate.endswith("@example.com"):
            raise ValueError("Registration using example.com emails is not allowed.")
        return validate

    # Sanitize email to prevent leading/trailing spaces
    @field_validator("email")
    def sanitize_email(cls, value: str) -> str:
        return value.strip().lower()

    # Santitize username to prevent special characters
    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric.")
        return value

    # Sanitize password to prevent common weak passwords
    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return value

    class Config:
        orm_mode = (True,)
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "mengsokheng0600@gmail.com",
                "password": "strongpassword123",
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = (True,)
        json_schema_extra = {
            "example": {
                "email": "mengsokheng0600@gmail.com",
                "password": "strongpassword123",
            }
        }


class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "email": "mengsokheng0600@gmail.com",
                "new_password": "newstrongpassword123",
                "confirm_password": "newstrongpassword123",
            }
        }


class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "old_password": "oldstrongpassword123",
                "new_password": "newstrongpassword123",
            }
        }


class UserProfile(BaseModel):
    id: int
    role: str
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LoginProfile(UserProfile):
    last_login: datetime

    class Config:
        orm_mode = True


class UserUpdateProfile(BaseModel):
    username: Optional[str] = None

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "username": "johndoe",
            }
        }


class EmailSchema(BaseModel):
    email: EmailStr
    username: Optional[str] = None

    class Config:
        orm_mode = True
