from fastapi import APIRouter, HTTPException, Request

from repositories.organization import SqlOrganizationRepository
from repositories.recruitment_pipeline import RecruitmentPipelineRepository
from services.authorization import build_authorization_context
from services.local_auth import get_request_principal

router = APIRouter(
    prefix="/api/recruitment",
    tags=["recruitment"],
)

_repository = RecruitmentPipelineRepository()
_organization_repository = SqlOrganizationRepository()

AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}

ALLOWED_ROLES = {"Administrator", "HR Manager", "Employer Manager"}


def _get_principal(request: Request) -> tuple[str, set[str]]:
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

    def claim_values(claim_type: str) -> set[str]:
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

    return principal_id, roles


@router.get("/pipeline")
def get_pipeline(request: Request):
    principal_id, roles = _get_principal(request)

    if not roles.intersection(ALLOWED_ROLES):
        raise HTTPException(
            status_code=403,
            detail="User is not authorized to view the recruitment pipeline",
        )

    memberships = _organization_repository.get_active_memberships(principal_id)

    context = build_authorization_context(
        user_id=principal_id,
        roles=roles,
        memberships=memberships,
    )

    return _repository.get_pipeline_counts(context)
