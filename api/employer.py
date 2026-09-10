import base64
import json

from fastapi import APIRouter, HTTPException, Request

from repositories.employer_dashboard import SqlEmployerDashboardRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context
from services.employer_dashboard import EmployerDashboardService


router = APIRouter(prefix="/api/employer", tags=["employer"])

_organization_repository = SqlOrganizationRepository()
_dashboard_repository = SqlEmployerDashboardRepository()
_service = EmployerDashboardService(_dashboard_repository)


AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}


def _get_principal(request: Request) -> tuple[str, str, set[str]]:
    principal_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME") or ""
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID") or ""
    encoded_principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not encoded_principal:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        padding = "=" * (-len(encoded_principal) % 4)
        principal = json.loads(
            base64.b64decode(encoded_principal + padding).decode("utf-8")
        )
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid authentication principal")

    claims = principal.get("claims", [])

    def claim_values(claim_type):
        return [
            claim.get("val")
            for claim in claims
            if claim.get("typ") == claim_type
        ]

    group_ids = set(claim_values("groups"))
    token_roles = set(claim_values("roles"))

    roles = set(token_roles)

    for role, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in group_ids:
            roles.add(role)

    if not roles:
        roles.add("Employee")

    employer_name = next(iter(claim_values("name")), principal_name)

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
            "new": dashboard.pipeline.new,
            "screening": dashboard.pipeline.screening,
            "shortlisted": dashboard.pipeline.shortlisted,
            "interview": dashboard.pipeline.interview,
            "offer": dashboard.pipeline.offer,
            "hired": dashboard.pipeline.hired,
        },
    }
