from typing import Optional
from pydantic import BaseModel
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    identifier: Optional[str] = None
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: Optional[str] = None
    name: str
    email: str
    role: UserRole
    pokja_id: Optional[int] = None


class UserBase(BaseModel):
    name: str
    username: Optional[str] = None
    email: str
    role: UserRole
    pokja_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

