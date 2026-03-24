"""Authentication dependencies for FastAPI routes."""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.core.auth import decode_token
from app.core.permissions import Permission, role_has_permissions
from app.core.permissions_store import get_user_overrides
from app.infrastructure.persistence.sql import UserRepo
from app.core.database import get_session
from app.application.services import UserService
from app.domain import User
from app.core.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_session),
):
    if settings.testing:
        # Tests that use FastAPI TestClient can bypass auth with a synthetic admin user.
        test_user = User(
            user_id=1,
            email="test-admin@example.com",
            hashed_password="not-used-in-testing",
            role="admin",
            full_name="Test Admin",
            is_active=True,
        )
        request.state.user = test_user
        return test_user

    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = creds.credentials
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    service = UserService(UserRepo(db))
    user = service.get_user(user_id)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    request.state.user = user
    return user


def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user


def require_permissions(*perms: Permission):
    """Dependency factory enforcing that current user has all required permissions.

    Usage: dependencies=[Depends(require_permissions(Permission.VIEW_PRODUCTS))]
    """
    def _checker(user=Depends(get_current_user)):
        # Admin bypasses fine-grained checks
        if user.role == "admin":
            return user
        required = set(perms)
        # Per-user overrides take precedence if present
        overrides = get_user_overrides(user.user_id)
        if overrides:
            allowed = overrides
            if not required.issubset(allowed):
                perm_names = ", ".join(p.value.replace("_", " ").title() for p in required - allowed)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail=f"You don't have permission to access this feature. Missing: {perm_names}. Please contact your administrator."
                )
            return user
        # Otherwise use role mapping
        if not role_has_permissions(user.role, required):
            perm_names = ", ".join(p.value.replace("_", " ").title() for p in required)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Access denied. Your role doesn't have permission for: {perm_names}. Please contact your administrator."
            )
        return user

    return _checker
