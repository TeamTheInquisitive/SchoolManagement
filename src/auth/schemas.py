from typing import Optional

import uuid

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    school_code: str
    avatar_url: str | None = None
    phone: str | None = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    user: UserResponse


class TokenRefreshResponse(BaseModel):
    message: str = "Token refreshed"


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str = "Password reset link sent to your email"


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str


class ResetPasswordResponse(BaseModel):
    message: str = "Password reset successfully"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class ChangePasswordResponse(BaseModel):
    message: str = "Password changed successfully"


class MessageResponse(BaseModel):
    message: str
