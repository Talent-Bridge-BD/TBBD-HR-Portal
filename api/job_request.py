import base64
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from models.job import Job

from models.job_request import JobRequest
from repositories.job import SqlJobRepository

from repositories.job_request import SqlJobRequestRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context

from services.local_auth import get_request_principal
from services.job import JobService

from services.job_request import JobRequestService

router = APIRouter(
    prefix="/api/job-requests",
    tags=["job-requests"],
)

_job_request_repository = SqlJobRequestRepository()
_job_request_service = JobRequestService(_job_request_repository)

_job_repository = SqlJobRepository()

_job_service = JobService(_job_repository)
_organization_repository = SqlOrganizationRepository()

EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


class JobRequestPayload(BaseModel):
    organization_id: str
    title: str
    description: str = ""
    employment_type: str = ""
    location: str = ""
    country: str = ""
    number_of_positions: int | None = None


def _claim_values(
    claims: list[dict],
    claim_type: str,
) -> set[str]:
    return {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == claim_type
        and claim.get("val")
    }


def get_job_request_authorization_context(request: Request):
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
    group_ids = _claim_values(claims, "groups")
    token_roles = _claim_values(claims, "roles")

    roles = set(token_roles)

    if EMPLOYER_MANAGER_GROUP_ID in group_ids:
        roles.add("Employer Manager")

    if HR_MANAGER_GROUP_ID in group_ids:
        roles.add("HR Manager")

    if ADMINISTRATOR_GROUP_ID in group_ids:
        roles.add("Administrator")

    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Employer management role is required",
        )

    memberships = _organization_repository.get_active_memberships(
        principal_id
    )

    return build_authorization_context(
        user_id=principal_id,
        roles=roles,
        memberships=memberships,
    )


def _require_organization_access(
    request: Request,
    organization_id: str,
):
    context = get_job_request_authorization_context(request)

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.get("")
async def list_job_requests(
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    requests = _job_request_service.list_requests(
        organization_id,
    )

    return {
        "requests": [
            item.__dict__
            for item in requests
        ]
    }


@router.get("/{request_id}")
async def get_job_request(
    request_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    job_request = _job_request_service.get_request(
        organization_id,
        request_id,
    )

    if job_request is None:
        raise HTTPException(
            status_code=404,
            detail="Job request not found",
        )

    return {
        "request": job_request.__dict__
    }


@router.post("")
async def create_job_request(
    payload: JobRequestPayload,
    request: Request,
):
    context = _require_organization_access(
        request,
        payload.organization_id,
    )

    job_request = JobRequest(
        id="",
        organization_id=payload.organization_id,
        requested_by=context.user_id,
        title=payload.title,
        description=payload.description or None,
        employment_type=payload.employment_type or None,
        location=payload.location or None,
        country=payload.country or None,
        number_of_positions=payload.number_of_positions,
        status="pending",
        requested_at=datetime.utcnow(),
    )

    saved = _job_request_service.save_request(
        job_request,
    )

    return {
        "request": saved.__dict__,
        "message": "Job request created",
    }

@router.post("/{request_id}/approve")
async def approve_job_request(
    request_id: str,
    organization_id: str,
    request: Request,
):
    context = _require_organization_access(
        request,
        organization_id,
    )

    if not context.roles.intersection(
        {"HR Manager", "Administrator"}
    ):
        raise HTTPException(
            status_code=403,
            detail="HR Manager or Administrator role is required",
        )

    job_request = _job_request_service.get_request(
        organization_id,
        request_id,
    )

    if job_request is None:
        raise HTTPException(
            status_code=404,
            detail="Job request not found",
        )

    if job_request.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Job request cannot be approved from "
                f"status '{job_request.status}'"
            ),
        )

    job = Job(
        id="",
        organization_id=job_request.organization_id,
        title=job_request.title,
        description=job_request.description,
        employment_type=job_request.employment_type,
        location=job_request.location,
        country=job_request.country,
        status="draft",
        number_of_positions=job_request.number_of_positions,
        work_location=job_request.location,
        employer_country=job_request.country,
    )

    saved_job = _job_service.save_job(job)

    approved_request = JobRequest(
        id=job_request.id,
        organization_id=job_request.organization_id,
        requested_by=job_request.requested_by,
        title=job_request.title,
        description=job_request.description,
        employment_type=job_request.employment_type,
        location=job_request.location,
        country=job_request.country,
        number_of_positions=job_request.number_of_positions,
        status="approved",
        requested_at=job_request.requested_at,
        reviewed_at=datetime.utcnow(),
        reviewed_by=context.user_id,
        created_at=job_request.created_at,
        updated_at=job_request.updated_at,
    )

    saved_request = _job_request_service.save_request(
        approved_request,
    )

    return {
        "request": saved_request.__dict__,
        "job": saved_job.__dict__,
        "message": "Job request approved and draft job created",
    }
