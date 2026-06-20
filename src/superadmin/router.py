from __future__ import annotations

import os
import time
import uuid

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from sqlalchemy import select

from src.auth.dependencies import SuperAdminUser
from src.core.config import settings as app_settings
from src.core.dependencies import SessionDep
from src.models.core import School
from src.superadmin import service
from src.superadmin.schemas import (
    AdminCreate,
    DashboardStatsResponse,
    HardDeleteResponse,
    PaymentCreate,
    PaymentListResponse,
    PaymentResponse,
    SchoolCreate,
    SchoolDetailResponse,
    SchoolListResponse,
    SchoolUpdate,
    SubscriptionCreate,
    SubscriptionHistoryResponse,
    SubscriptionResponse,
    SubscriptionStatusUpdate,
    SubscriptionUpdate,
    UserListResponse,
)

router = APIRouter(prefix="/superadmin", tags=["Super Admin"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: SessionDep, user: SuperAdminUser):
    return await service.get_dashboard_stats(db)


@router.get("/schools", response_model=SchoolListResponse)
async def list_schools(db: SessionDep, user: SuperAdminUser):
    return await service.get_schools(db)


@router.post("/schools", response_model=SchoolDetailResponse, status_code=201)
async def create_school(db: SessionDep, user: SuperAdminUser, data: SchoolCreate):
    school = await service.create_school(db, data.model_dump(exclude_none=True))
    detail = await service.get_school_detail(db, school.id)
    return detail


@router.get("/schools/{school_id}", response_model=SchoolDetailResponse)
async def get_school_detail(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID):
    detail = await service.get_school_detail(db, school_id)
    if not detail:
        raise HTTPException(status_code=404, detail="School not found")
    return detail


@router.put("/schools/{school_id}", response_model=SchoolDetailResponse)
async def update_school(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: SchoolUpdate):
    school = await service.update_school(db, school_id, data.model_dump(exclude_none=True))
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    detail = await service.get_school_detail(db, school.id)
    return detail


@router.delete("/schools/{school_id}/hard-delete", response_model=HardDeleteResponse)
async def hard_delete_school(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID):
    """Permanently delete ALL data related to a school. This is irreversible."""
    result = await service.hard_delete_school(db, school_id)
    if not result:
        raise HTTPException(status_code=404, detail="School not found")
    return result


@router.post("/schools/{school_id}/logo")
async def upload_school_logo(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, file: UploadFile = File(...)):
    """Upload or update a school's logo (superadmin)."""
    # Validate file type
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: png, jpg, jpeg, webp")

    # Validate file extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("png", "jpg", "jpeg", "webp"):
        raise HTTPException(status_code=400, detail="Invalid file extension. Allowed: png, jpg, jpeg, webp")

    # Read file and validate size (2MB limit)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 2MB")

    # Ensure upload directory exists
    logos_dir = os.path.join(app_settings.UPLOAD_DIR, "logos")
    os.makedirs(logos_dir, exist_ok=True)

    # Save file
    filename = f"{school_id}_{int(time.time())}.{ext}"
    filepath = os.path.join(logos_dir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    # Update school logo_url in database
    logo_url = f"/uploads/logos/{filename}"
    result = await db.execute(select(School).where(School.id == school_id))
    school_obj = result.scalar_one_or_none()
    if not school_obj:
        raise HTTPException(status_code=404, detail="School not found")
    school_obj.logo_url = logo_url
    await db.commit()

    return {"logo_url": logo_url}


# --- Subscription Status (trial dates, status) ---

@router.put("/schools/{school_id}/subscription-status", response_model=SchoolDetailResponse)
async def update_subscription_status(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: SubscriptionStatusUpdate):
    school = await service.update_subscription_status(db, school_id, data.model_dump(exclude_none=True))
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    detail = await service.get_school_detail(db, school.id)
    return detail


# --- Subscriptions ---

@router.get("/schools/{school_id}/subscription", response_model=SubscriptionResponse | None)
async def get_subscription(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID):
    sub = await service.get_subscription(db, school_id)
    if not sub:
        return None
    return {
        "id": sub.id, "plan_type": sub.plan_type, "amount": float(sub.amount),
        "start_date": sub.start_date, "end_date": sub.end_date,
        "auto_renew": sub.auto_renew, "is_active": sub.is_active,
        "created_at": sub.created_at,
    }


@router.get("/schools/{school_id}/subscription-history", response_model=SubscriptionHistoryResponse)
async def get_subscription_history(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID):
    return await service.get_subscription_history(db, school_id)


@router.post("/schools/{school_id}/subscription", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: SubscriptionCreate):
    sub = await service.create_subscription(db, school_id, data.model_dump())
    return {
        "id": sub.id, "plan_type": sub.plan_type, "amount": float(sub.amount),
        "start_date": sub.start_date, "end_date": sub.end_date,
        "auto_renew": sub.auto_renew, "is_active": sub.is_active,
        "created_at": sub.created_at,
    }


@router.put("/schools/{school_id}/subscription", response_model=SubscriptionResponse)
async def update_subscription(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: SubscriptionUpdate):
    sub = await service.update_subscription(db, school_id, data.model_dump(exclude_none=True))
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return {
        "id": sub.id, "plan_type": sub.plan_type, "amount": float(sub.amount),
        "start_date": sub.start_date, "end_date": sub.end_date,
        "auto_renew": sub.auto_renew, "is_active": sub.is_active,
        "created_at": sub.created_at,
    }


# --- Payments ---

@router.get("/schools/{school_id}/payments", response_model=PaymentListResponse)
async def list_payments(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID):
    return await service.get_payments(db, school_id)


@router.post("/schools/{school_id}/payments", response_model=PaymentResponse, status_code=201)
async def create_payment(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: PaymentCreate):
    try:
        payment = await service.create_payment(db, school_id, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "id": payment.id, "subscription_id": payment.subscription_id,
        "amount": float(payment.amount), "payment_date": payment.payment_date,
        "period_start": payment.period_start, "period_end": payment.period_end,
        "status": payment.status, "notes": payment.notes, "created_at": payment.created_at,
    }


# --- Admin Users ---

@router.post("/schools/{school_id}/admin", status_code=201)
async def create_school_admin(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: AdminCreate):
    admin = await service.create_admin_for_school(db, school_id, data.model_dump())
    return {"id": admin.id, "email": admin.email, "full_name": admin.full_name, "role": admin.role}


# --- Platform Settings ---

@router.get("/settings")
async def get_platform_settings(db: SessionDep, user: SuperAdminUser):
    from src.models.platform_settings import PlatformSettings
    result = await db.execute(select(PlatformSettings))
    settings = result.scalars().all()
    return {s.key: s.value for s in settings}


@router.put("/settings")
async def update_platform_settings(db: SessionDep, user: SuperAdminUser, data: dict):
    from src.models.platform_settings import PlatformSettings
    for key, value in data.items():
        result = await db.execute(select(PlatformSettings).where(PlatformSettings.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            db.add(PlatformSettings(key=key, value=value))
    await db.commit()
    return {"status": "updated"}


# --- Users ---

@router.get("/users", response_model=UserListResponse)
async def list_users(
    db: SessionDep,
    user: SuperAdminUser,
    role: str | None = Query(default=None),
    school_id: uuid.UUID | None = Query(default=None),
):
    return await service.get_users(db, role=role, school_id=school_id)


@router.post("/users/{user_id}/unlock")
async def unlock_user(
    user_id: uuid.UUID,
    db: SessionDep,
    user: SuperAdminUser,
):
    """Unlock a locked user account and reset failed attempts."""
    from src.models.core import User
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        from src.core.exceptions import NotFound
        raise NotFound("User", str(user_id))
    target_user.is_locked = False
    target_user.failed_login_attempts = 0
    await db.commit()
    return {"message": f"User {target_user.email} unlocked successfully", "user_id": str(user_id), "email": target_user.email}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: uuid.UUID,
    data: dict,
    db: SessionDep,
    user: SuperAdminUser,
):
    """Reset a user's password (superadmin override)."""
    from src.models.core import User
    from src.core.security import hash_password
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        from src.core.exceptions import NotFound
        raise NotFound("User", str(user_id))
    new_password = data.get("password")
    if not new_password or len(new_password) < 4:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
    target_user.password_hash = hash_password(new_password)
    target_user.is_locked = False
    target_user.failed_login_attempts = 0
    target_user.password_changed = False
    await db.commit()
    return {"message": f"Password reset for {target_user.email}", "user_id": str(user_id), "email": target_user.email}
