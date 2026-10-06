from fastapi import APIRouter, Request, Query

from api.administrator import _get_administrator_context
from repositories.audit_logs import AuditLogRepository


router = APIRouter(
    prefix="/api/administrator",
    tags=["administrator-activity"],
)


_audit_log_repository = AuditLogRepository()


@router.get("/activity")
def get_administrator_activity(
    request: Request,
    limit: int = Query(default=100, ge=1, le=500),
):
    _get_administrator_context(request)

    return {
        "activities": _audit_log_repository.list_recent(
            limit=limit
        ),
        "failedEvents": _audit_log_repository.count_recent_failures(),
    }
