from fastapi import APIRouter, HTTPException, Request

from repositories.organization import SqlOrganizationRepository
from repositories.recruitment_pipeline import RecruitmentPipelineRepository
from services.authorization import build_authorization_context_from_principal
from services.local_auth import get_request_principal

router = APIRouter(
    prefix="/api/recruitment",
    tags=["recruitment"],
)

_repository = RecruitmentPipelineRepository()
_organization_repository = SqlOrganizationRepository()


ALLOWED_ROLES = {"Administrator", "HR Manager", "Employer Manager"}


def _get_principal(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    return str(principal["id"]), principal


@router.get("/pipeline")
def get_pipeline(request: Request):
    principal_id, principal = _get_principal(request)

    preliminary_context = build_authorization_context_from_principal(
        principal,
        [],
    )

    if not preliminary_context.roles.intersection(ALLOWED_ROLES):
        raise HTTPException(
            status_code=403,
            detail="User is not authorized to view the recruitment pipeline",
        )

    memberships = _organization_repository.get_active_memberships(principal_id)
    context = build_authorization_context_from_principal(
        principal,
        memberships,
    )

    return _repository.get_pipeline_counts(context)
