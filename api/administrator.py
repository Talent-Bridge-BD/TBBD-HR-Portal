from fastapi import APIRouter, HTTPException, Request

from repositories.organization import SqlOrganizationRepository
from repositories.application_roles import application_role_repository
from repositories.user_profile import SqlUserProfileRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/administrator",
    tags=["administrator"],
)


_organization_repository = SqlOrganizationRepository()
_user_profile_repository = SqlUserProfileRepository()


AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}


def _get_administrator_context(request: Request):
    principal = get_request_principal(request)
    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user required",
        )

    principal_id = str(principal["id"])
    principal_email = str(principal.get("email") or "").strip()
    user_id = principal_id

    claims = principal.get("claims") or []
    valid_claims = [claim for claim in claims if isinstance(claim, dict)]

    roles = {
        str(claim.get("val") or "").strip()
        for claim in valid_claims
        if str(claim.get("typ") or "").strip().lower().endswith("roles")
        and claim.get("val")
    }

    group_ids = {
        str(claim.get("val") or "").strip()
        for claim in valid_claims
        if str(claim.get("typ") or "").strip().lower().endswith("groups")
        and claim.get("val")
    }

    for role_name, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in group_ids:
            roles.add(role_name)

    if "Administrator" not in roles:
        if principal_email:
            try:
                profile = _user_profile_repository.get_by_email(principal_email)
            except ValueError:
                raise HTTPException(
                    status_code=409,
                    detail="Multiple user profiles match the signed-in email.",
                )

            if profile is not None:
                user_id = str(profile.user_id)

        try:
            if application_role_repository.has_role(user_id, "Administrator"):
                roles.add("Administrator")
        except Exception as ex:
            print(
                f"[ADMIN ROLE LOOKUP FAILED] {type(ex).__name__}: {ex}",
                flush=True,
            )

    memberships = _organization_repository.get_active_memberships(user_id)
    context = build_authorization_context(
        user_id=user_id,
        roles=roles,
        memberships=memberships,
    )

    if not is_global_administrator(context):
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return context


@router.get("/dashboard")
def get_administrator_dashboard(
    request: Request,
):

    _get_administrator_context(request)

    organizations = (
        _organization_repository.list_active_organizations()
    )

    members = (
        _organization_repository.list_all_members()
    )

    return {
        "organizations": {
            "total": len(organizations),
            "active": len(
                [
                    org
                    for org in organizations
                    if org.status == "active"
                ]
            ),
        },

        "users": {
            "total": len(
                set(
                    member.user_id
                    for member in members
                )
            ),
            "active": len(
                set(
                    member.user_id
                    for member in members
                    if member.status == "active"
                )
            ),
        },

        "roles": {
            "total": 4,
            "permissionSets": 0,
        },

        "notifications": {
            "templates": 0,
            "deliveryStatus": 0,
        },

        "system": {
            "settings": None,
            "integrations": None,
        },
    }