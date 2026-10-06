from fastapi import APIRouter, Request

from repositories.administrator_notifications import (
    AdministratorNotificationRepository,
)

from services.administrator_notifications import (
    AdministratorNotificationService,
)

from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/administrator/notifications",
    tags=["administrator notifications"],
)


_repository = AdministratorNotificationRepository()

_service = AdministratorNotificationService(
    _repository
)


def _require_administrator(request: Request):

    principal = get_request_principal(request)

    if not principal:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    roles = principal.get("roles") or []

    if "Administrator" not in roles:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return principal


@router.get("/email-settings")
def get_email_settings(
    request: Request,
):

    _require_administrator(request)

    return _service.get_email_settings()


@router.get("/templates")
def list_templates(
    request: Request,
):

    _require_administrator(request)

    return _service.list_templates()


@router.get("/delivery-logs")
def list_delivery_logs(
    request: Request,
    limit: int = 100,
):

    _require_administrator(request)

    return _service.list_delivery_logs(
        limit=limit
    )