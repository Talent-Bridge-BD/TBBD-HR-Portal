import base64
import json

from fastapi import APIRouter, HTTPException, Request

from repositories.employer_dashboard import SqlEmployerDashboardRepository
from repositories.organization import SqlOrganizationRepository
from repositories.external_identity import SqlExternalIdentityMappingRepository
from services.authorization import build_authorization_context
from services.local_auth import (
    TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER,
    TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
    get_request_principal,
    is_employer_external_principal,
    has_external_employer_manager_group,
)
from services.employer_dashboard import EmployerDashboardService


router = APIRouter(prefix="/api/employer", tags=["employer"])

_organization_repository = SqlOrganizationRepository()
_identity_mapping_repository = SqlExternalIdentityMappingRepository(
    _organization_repository._connection
)
_dashboard_repository = SqlEmployerDashboardRepository()
_service = EmployerDashboardService(_dashboard_repository)


AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}


def _get_principal(request: Request) -> tuple[str, str, set[str], dict]:
    principal = get_request_principal(request)

    if not principal:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    principal_id = principal.get("id")
    if not principal_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    # Use the normalized claims provided by local_auth.
    claims = principal.get("claims", [])

    def raw_claim_values(claim_type):
        return {
            str(claim.get("val"))
            for claim in claims
            if isinstance(claim, dict)
            and claim.get("typ") == claim_type
            and claim.get("val")
        }

    group_ids = set(principal.get("groups") or [])
    token_roles = set(principal.get("roles") or [])

    if not group_ids:
        group_ids = raw_claim_values("groups")
    if not token_roles:
        token_roles = raw_claim_values("roles")

    role_aliases = {
        "Employer.Manager": "Employer Manager",
    }

    roles = {
        role_aliases.get(role, role)
        for role in token_roles
    }

    for role, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in group_ids:
            roles.add(role)

    if not roles:
        roles.add("Employee")

    employer_name = (
        principal.get("name")
        or principal.get("email")
        or "Employer"
    )

    return principal_id, employer_name, roles, principal

@router.get("/dashboard")
async def get_employer_dashboard(request: Request):
    principal_id, employer_name, roles, principal = _get_principal(request)

    if str(principal.get("tenant_id") or "").lower() == (
        TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID.lower()
    ):
        if not is_employer_external_principal(principal):
            raise HTTPException(
                status_code=401,
                detail="Employer External ID application audience is invalid",
            )

        if not has_external_employer_manager_group(principal):
            raise HTTPException(
                status_code=403,
                detail="External Employer Manager group membership is required",
            )

        external_object_id = str(principal.get("object_id") or "").strip()
        if not external_object_id:
            raise HTTPException(
                status_code=401,
                detail="Employer External ID object identity is missing",
            )

        mapping = _identity_mapping_repository.get_mapping(
            provider=TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER,
            tenant_id=TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
            external_object_id=external_object_id,
        )
        if mapping is not None:
            if str(mapping.get("status", "")).lower() != "active":
                raise HTTPException(
                    status_code=403,
                    detail="Employer identity mapping is not active",
                )
            application_user_id = str(mapping.get("application_user_id") or "")
            if not application_user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Employer identity is not linked to an application account",
                )
        else:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Employer external identity has not been linked "
                    "to an application account"
                ),
            )

        memberships = _organization_repository.get_active_memberships(
            application_user_id
        )
        if not any(
            str(membership.role).strip().lower() == "employer manager"
            and str(membership.status).strip().lower() == "active"
            for membership in memberships
        ):
            raise HTTPException(
                status_code=403,
                detail="An active Employer Manager organization membership is required",
            )
        principal_id = application_user_id
        roles = {"Employer Manager"}
    else:
        memberships = _organization_repository.get_active_memberships(
            principal_id
        )

    context = build_authorization_context(
        user_id=principal_id,
        roles=roles,
        memberships=memberships,
    )

    try:
        dashboard = _service.get_dashboard(
            context=context,
            employer_name=employer_name,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return {
        "employer_name": dashboard.employer_name,
        "organization_name": dashboard.organization_name,
        "stats": {
            "active_jobs": dashboard.stats.active_jobs,
            "new_applications": dashboard.stats.new_applications,
            "candidates_pipeline": dashboard.stats.candidates_pipeline,
            "interviews_upcoming": dashboard.stats.interviews_upcoming,
        },
        "pipeline": {
            "applied": dashboard.pipeline.applied,
            "screening": dashboard.pipeline.screening,
            "interview": dashboard.pipeline.interview,
            "trade_test": dashboard.pipeline.trade_test,
            "medical": dashboard.pipeline.medical,
            "visa_processing": dashboard.pipeline.visa_processing,
            "ticketing": dashboard.pipeline.ticketing,
            "onboarding": dashboard.pipeline.onboarding,
            "deployment": dashboard.pipeline.deployment,
            "completed": dashboard.pipeline.completed,
        },
    }
