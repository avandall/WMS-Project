"""AI endpoints (LangChain)."""

from fastapi import APIRouter, Depends, HTTPException

from app.ai_engine import handle_customer_chat_with_db
from app.api.auth_deps import get_current_user, require_permissions
from app.core.permissions import Permission

from ..schemas.ai import ChatDBRequest, ChatDBResponse

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/ai/chat-db",
    response_model=ChatDBResponse,
    dependencies=[Depends(require_permissions(Permission.VIEW_REPORTS))],
)
async def chat_db(payload: ChatDBRequest):
    """Chat with the database using natural language (read-only queries)."""

    try:
        result = handle_customer_chat_with_db(payload.message)
        if not payload.include_rows:
            result["rows"] = None
        return ChatDBResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        detail = str(e) or type(e).__name__
        raise HTTPException(
            status_code=502,
            detail=f"AI engine error ({type(e).__name__}): {detail}",
        )
