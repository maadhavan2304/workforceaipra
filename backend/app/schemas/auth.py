from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.user import RoleEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: RoleEnum = RoleEnum.EMPLOYEE
    employee_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: RoleEnum
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
