"""User management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.auth_deps import get_current_user, require_permissions
from app.core.permissions import Permission, ROLE_PERMISSIONS, Permission as PermEnum
from app.core.permissions_store import set_user_overrides, clear_user_overrides
from app.api.schemas.auth import UserCreate, UserResponse
from app.repositories.sql.user_repo import UserRepo
from app.services.user_service import UserService
from app.core.database import get_session

router = APIRouter()


def get_user_service(db=Depends(get_session)) -> UserService:
    return UserService(UserRepo(db))


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return UserResponse.from_domain(user)


@router.get(
    "/",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permissions(Permission.MANAGE_USERS))],
)
async def list_users(service: UserService = Depends(get_user_service)):
    users = service.list_users()
    return [UserResponse.from_domain(u) for u in users.values()]


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    dependencies=[Depends(require_permissions(Permission.MANAGE_USERS))],
)
async def create_user(payload: UserCreate, service: UserService = Depends(get_user_service)):
    user = service.create_user(email=payload.email, password=payload.password, role=payload.role, full_name=payload.full_name)
    return UserResponse.from_domain(user)


@router.get(
    "/permissions",
    dependencies=[Depends(require_permissions(Permission.MANAGE_USERS))],
)
async def list_permissions():
    return {
        "permissions": [p.value for p in PermEnum],
        "roles": {role: [p.value for p in perms] for role, perms in ROLE_PERMISSIONS.items()},
    }


class RoleUpdatePayload(BaseModel):
    role: str


@router.patch(
    "/{user_id}/role",
    dependencies=[Depends(require_permissions(Permission.MANAGE_USERS))],
)
async def update_role(user_id: int, payload: RoleUpdatePayload, service: UserService = Depends(get_user_service)):
    user = service.update_role(user_id, payload.role)
    return UserResponse.from_domain(user)


class PermissionsUpdatePayload(BaseModel):
    permissions: list[str] | None = None
    mode: str = "override"  # "override" to set, "clear" to remove overrides


@router.patch(
    "/{user_id}/permissions",
    dependencies=[Depends(require_permissions(Permission.MANAGE_USERS))],
)
async def update_permissions(user_id: int, payload: PermissionsUpdatePayload):
    if payload.mode == "clear":
        clear_user_overrides(user_id)
    else:
        set_user_overrides(user_id, payload.permissions or [])
    return {"user_id": user_id, "status": "ok"}


class ChangePasswordPayload(BaseModel):
    old_password: str
    new_password: str


@router.post("/me/change-password")
async def change_my_password(
    payload: ChangePasswordPayload,
    user=Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Change current user's password."""
    service.change_password(user.user_id, payload.old_password, payload.new_password)
    return {"status": "ok", "message": "Password changed successfully"}


@router.post(
    "/{user_id}/reset-password",
    dependencies=[Depends(require_permissions(Permission.MANAGE_USERS))],
)
async def reset_user_password(
    user_id: int,
    payload: BaseModel,
    service: UserService = Depends(get_user_service),
):
    """Admin can reset any user's password (bypasses old password check)."""
    from pydantic import Field
    class ResetPayload(BaseModel):
        new_password: str = Field(min_length=6)
    
    reset_payload = ResetPayload(**payload.model_dump())
    user = service.get_user(user_id)
    from app.core.auth import hash_password as hp
    from app.models.user_domain import User as U
    updated = U(
        user_id=user.user_id,
        email=user.email,
        hashed_password=hp(reset_payload.new_password),
        role=user.role,
        full_name=user.full_name,
        is_active=user.is_active,
    )
    service.user_repo.save(updated)
    return {"status": "ok", "message": "Password reset successfully"}
