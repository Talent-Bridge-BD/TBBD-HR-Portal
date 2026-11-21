from fastapi import APIRouter, HTTPException, Request

from repositories.employer_dashboard import SqlEmployerDashboardRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context_from_principal
from services.local_auth import get_request_principal
from services.employer_dashboard import EmployerDashboardService


router = APIRouter(prefix="/api/employer", tags=["employer"])

_organization_repository = SqlOrganizationRepository()
_dashboard_repository = SqlEmployerDashboardRepository()
_service = EmployerDashboardService(_dashboard_repository)


def _get_principal(request: Request):
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

    memberships = _organization_repository.get_active_memberships(
        principal_id
    )

    context = build_authorization_context_from_principal(
        principal=principal,
        memberships=memberships,
    )

    employer_name = (
        principal.get("name")
        or principal.get("email")
        or "Employer"
    )

    return principal_id, employer_name, context


@router.get("/dashboard")
async def get_employer_dashboard(request: Request):
    _, employer_name, context = _get_principal(request)

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
