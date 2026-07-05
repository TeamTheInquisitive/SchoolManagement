from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, Header, Response, Request
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import service as auth_service
from src.auth.dependencies import CurrentUser
from src.auth.schemas import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenRefreshResponse,
    UserResponse,
)
from src.core.config import settings
from src.core.database import get_db
from src.core.redis import get_redis
from src.models.core import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set httpOnly cookies for access and refresh tokens."""
    is_local = settings.ENVIRONMENT == "local"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not is_local,
        samesite="lax" if is_local else "none",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not is_local,
        samesite="lax" if is_local else "none",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def _clear_auth_cookies(response: Response) -> None:
    """Clear auth cookies."""
    is_local = settings.ENVIRONMENT == "local"
    response.delete_cookie(key="access_token", samesite="lax" if is_local else "none", secure=not is_local)
    response.delete_cookie(key="refresh_token", path="/api/v1/auth", samesite="lax" if is_local else "none", secure=not is_local)


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    x_school_code: str | None = Header(default=None, alias="X-School-Code"),
) -> LoginResponse:
    """Authenticate user and set httpOnly cookies."""
    from datetime import date
    from src.core.exceptions import AccessDenied
    from src.models.core import School
    from src.models.subscription import Subscription

    school_id = None
    if x_school_code:
        result = await db.execute(
            select(School).where(School.code == x_school_code, School.is_active.is_(True))
        )
        school = result.scalar_one_or_none()
        if school:
            school_id = school.id
    user = await auth_service.authenticate_user(
        db, data.identifier or data.email, data.password, school_id, username=data.username
    )

    # Portal-based access control: prevent cross-account login
    if data.portal:
        portal_role_map = {
            "admin": "admin",
            "teacher": "teacher",
            "student": "student",
            "superadmin": "super_admin",
        }
        expected_role = portal_role_map.get(data.portal)
        if expected_role and user.role != expected_role:
            raise AccessDenied(
                "This account doesn't have access to this portal. Please use the correct portal."
            )

    # Skip subscription check for super_admin
    if user.role != "super_admin":
        school_obj = user.school
        if school_obj and school_obj.subscription_status == "expired":
            grace_days = school_obj.grace_period_days or 2
            today = date.today()

            # Find when subscription expired
            sub_result = await db.execute(
                select(Subscription).where(Subscription.school_id == school_obj.id)
                .order_by(Subscription.end_date.desc())
            )
            last_sub = sub_result.scalars().first()

            if last_sub:
                days_since_expiry = (today - last_sub.end_date).days
                if days_since_expiry > grace_days:
                    raise AccessDenied("Your subscription has expired. Please contact the administrator to renew.")
            elif school_obj.trial_end_date:
                days_since_trial_end = (today - school_obj.trial_end_date).days
                if days_since_trial_end > grace_days:
                    raise AccessDenied("Your free trial has expired. Please contact the administrator to activate your subscription.")

    access_token, refresh_token = auth_service.create_tokens(user)

    _set_auth_cookies(response, access_token, refresh_token)

    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        school_code=user.school.code if user.school else None,
        avatar_url=user.avatar_url,
    )
    return LoginResponse(user=user_response)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    redis: Redis = Depends(get_redis),
    refresh_token: str | None = Cookie(default=None),
) -> LogoutResponse:
    """Logout user - blacklist refresh token and clear cookies."""
    if refresh_token:
        await auth_service.logout_user(redis, refresh_token)
    _clear_auth_cookies(response)
    return LogoutResponse()


@router.post("/refresh-token", response_model=TokenRefreshResponse)
async def refresh_token(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    refresh_token: str | None = Cookie(default=None),
) -> TokenRefreshResponse:
    """Refresh the access token using the refresh token cookie."""
    from src.core.exceptions import AuthenticationError

    if not refresh_token:
        raise AuthenticationError("No refresh token provided")

    new_access_token, new_refresh_token = await auth_service.refresh_access_token(
        db, redis, refresh_token
    )
    _set_auth_cookies(response, new_access_token, new_refresh_token)
    return TokenRefreshResponse()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """Get the current authenticated user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        school_code=current_user.school.code if current_user.school else None,
        avatar_url=current_user.avatar_url,
        phone=current_user.phone,
    )


@router.get("/school-profile")
async def get_school_profile_for_user(current_user: CurrentUser):
    """Get school profile for any authenticated user."""
    school = current_user.school
    return {
        "school_name": school.name if school else None,
        "code": school.code if school else None,
        "logo_url": school.logo_url if school else None,
        "email": school.email if school else None,
        "phone": school.phone if school else None,
    }


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    """Send a password reset link to the user's email."""
    await auth_service.initiate_password_reset(db, data.email)
    return ForgotPasswordResponse()


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ResetPasswordResponse:
    """Reset password using the token from the email link."""
    await auth_service.reset_password(db, data.token, data.new_password, data.confirm_password)
    return ResetPasswordResponse()


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ChangePasswordResponse:
    """Change password for the currently authenticated user."""
    await auth_service.change_password(
        db, current_user, data.current_password, data.new_password, data.confirm_password
    )
    return ChangePasswordResponse()
