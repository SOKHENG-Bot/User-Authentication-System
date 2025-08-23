from pydantic import BaseModel, EmailStr, Field


class RegisterForm(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

    class Config:
        orm_mode = True


class ShowUserAccount(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    is_verified: str

    class Config:
        orm_mode = True
