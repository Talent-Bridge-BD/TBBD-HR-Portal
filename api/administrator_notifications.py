from fastapi import APIRouter, HTTPException, Request

from repositories.administrator_notifications import (
    AdministratorNotificationRepository,
)

from services.administrator_notifications import (
    AdministratorNotificationService,
)

from services.local_auth import get_request_principal
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from repositories.organization import SqlOrganizationRepository


router = APIRouter(
    prefix="/api/administrator/notifications",
    tags=["administrator notifications"],
)


_repository = AdministratorNotificationRepository()
_organization_repository = SqlOrganizationRepository()

_service = AdministratorNotificationService(
    _repository
)


def _require_administrator(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user required",
        )

    claims = principal.get("claims", [])

    group_ids = {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == "groups"
        and claim.get("val")
    }

    roles_claim = {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == "roles"
        and claim.get("val")
    }

    roles = set(roles_claim)

    if "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66" in group_ids:
        roles.add("Administrator")

    context = build_authorization_context(
        user_id=principal["id"],
        roles=roles,
        memberships=_organization_repository.get_active_memberships(
            principal["id"]
        ),
    )

    if not is_global_administrator(context):
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return context


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