from fastapi import APIRouter, HTTPException, Request

from repositories.notifications import SqlNotificationRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    AUTHORIZATION_GROUPS,
    build_authorization_context,
)
from services.local_auth import get_request_principal
from services.notifications import NotificationService


router = APIRouter(
    prefix="/api/notifications",
    tags=["notifications"],
)

_notification_repository = SqlNotificationRepository()
_notification_service = NotificationService(
    _notification_repository
)
_organization_repository = SqlOrganizationRepository()


def _get_authorization_context(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user is required",
        )

    principal_id = principal["id"]

    groups = principal.get("groups") or []
    roles = principal.get("roles") or []

    resolved_roles = set(roles)

    for role_name, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in groups:
            resolved_roles.add(role_name)

    memberships = (
        _organization_repository.get_active_memberships(
            principal_id
        )
    )

    return build_authorization_context(
        user_id=principal_id,
        roles=resolved_roles,
        memberships=memberships,
    )


@router.get("")
def list_notifications(
    request: Request,
    limit: int = 50,
):
    context = _get_authorization_context(request)

    organization_ids = None

    if (
        not context.is_global_administrator
        and "Candidate" not in context.roles
    ):
        organization_ids = set(context.organization_ids)

    return _notification_service.list_notifications(
        recipient_user_id=context.user_id,
        organization_ids=organization_ids,
        limit=limit,
    )


@router.get("/unread-count")
def unread_count(request: Request):
    context = _get_authorization_context(request)

    organization_ids = None

    if (
        not context.is_global_administrator
        and "Candidate" not in context.roles
    ):
        organization_ids = set(context.organization_ids)

    return {
        "count": _notification_service.unread_count(
            recipient_user_id=context.user_id,
            organization_ids=organization_ids,
        )
    }


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    request: Request,
):
    context = _get_authorization_context(request)

    notification = _notification_service.mark_read(
        notification_id=notification_id,
        recipient_user_id=context.user_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return notification


@router.patch("/read-all")
def mark_all_notifications_read(
    request: Request,
):
    context = _get_authorization_context(request)

    organization_ids = None

    if (
        not context.is_global_administrator
        and "Candidate" not in context.roles
    ):
        organization_ids = set(context.organization_ids)

    affected = _notification_service.mark_all_read(
        recipient_user_id=context.user_id,
        organization_ids=organization_ids,
    )

    return {
        "updated": affected,
    }