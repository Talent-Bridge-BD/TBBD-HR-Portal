import base64
import json

from fastapi import APIRouter, HTTPException, Request

from repositories.employer_dashboard import SqlEmployerDashboardRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context
from services.local_auth import get_request_principal
from services.employer_dashboard import EmployerDashboardService


router = APIRouter(prefix="/api/employer", tags=["employer"])

_organization_repository = SqlOrganizationRepository()
_dashboard_repository = SqlEmployerDashboardRepository()
_service = EmployerDashboardService(_dashboard_repository)


AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}


def _get_principal(request: Request) -> tuple[str, str, set[str]]:
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

    claims = principal.get("claims", [])

    def claim_values(claim_type):
        return {
            str(claim.get("val"))
            for claim in claims
            if claim.get("typ") == claim_type and claim.get("val")
        }

    group_ids = claim_values("groups")
    token_roles = claim_values("roles")

    roles = set(token_roles)

    for role, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in group_ids:
            roles.add(role)

    if not roles:
        roles.add("Employee")

    employer_name = principal.get("name") or principal.get("email") or "Employer"

    return principal_id, employer_name, roles


@router.get("/dashboard")
async def get_employer_dashboard(request: Request):
    principal_id, employer_name, roles = _get_principal(request)

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
