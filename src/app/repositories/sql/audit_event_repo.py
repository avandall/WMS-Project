from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger, request_id_ctx
from app.core.transaction import TransactionalRepository
from app.repositories.sql.models import AuditEventModel

logger = get_logger(__name__)


class AuditEventRepo(TransactionalRepository):
    """Repository for domain audit events (business-level audit trail)."""

    def __init__(self, session: Session):
        super().__init__(session)

    def create_event(
        self,
        *,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> int:
        event = AuditEventModel(
            request_id=request_id_ctx.get(),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            warehouse_id=warehouse_id,
            payload=payload,
        )
        self.session.add(event)
        self._commit_if_auto()
        logger.info(
            f"Audit event: action={action} entity_type={entity_type} entity_id={entity_id} warehouse_id={warehouse_id}"
        )
        return event.id

