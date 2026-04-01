"""User domain model and validation."""
from typing import Optional
from app.exceptions.business_exceptions import ValidationError
from app.core.error_constants import ErrorMessages


class User:
    def __init__(self, user_id: int, email: str, hashed_password: str, role: str = "user", full_name: Optional[str] = None, is_active: bool = True):
        self._validate_email(email)
        self._validate_role(role)
        self.user_id = user_id
        self.email = email.lower()
        self.hashed_password = hashed_password
        self.role = role
        self.full_name = full_name
        self.is_active = is_active

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email or "@" not in email:
            raise ValidationError(ErrorMessages.INVALID_EMAIL if hasattr(ErrorMessages, "INVALID_EMAIL") else "Invalid email")

    @staticmethod
    def _validate_role(role: str) -> None:
        allowed = {"admin", "user", "sales", "warehouse", "accountant"}
        if role not in allowed:
            raise ValidationError(f"Role must be one of: {', '.join(sorted(allowed))}")
