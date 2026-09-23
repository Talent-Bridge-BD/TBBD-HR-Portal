import base64
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from models.job import Job
from repositories.job import SqlJobRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    AUTHORIZATION_GROUPS,
    build_authorization_context,
    is_global_administrator,
)
from services.job import JobService
from services.local_auth import get_request_principal


router = APIRouter(prefix="/api/jobs", tags=["jobs"])

_job_repository = SqlJobRepository()
_job_service = JobService(_job_repository)
_organization_repository = SqlOrganizationRepository()

EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


class JobRequest(BaseModel):
    organization_id: str
    title: str
    description: str = ""
    employment_type: str = ""
    location: str = ""
    country: str = ""
    status: str = "draft"
    number_of_positions: int | None = None
    published_at: datetime | None = None
    closing_at: datetime | None = None

    # Overseas recruitment core fields
    requisition_number: str = ""
    employer_name: str = ""
    employer_country: str = ""
    employer_city: str = ""
    trade_skill_category: str = ""
    industry_sector: str = ""
    gender_requirement: str = ""
    minimum_age: int | None = None
    maximum_age: int | None = None
    contract_duration: str = ""
    work_location: str = ""
    project_name: str = ""


def _claim_values(claims: list[dict], claim_type: str) -> set[str]:
    return {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == claim_type and claim.get("val")
    }


def get_job_authorization_context(request: Request):

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

    for role, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in group_ids:
            roles.add(role)
    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Recruitment management role is required",
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
    context = get_job_authorization_context(request)

    if is_global_administrator(context):
        return context

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.get("")
async def list_jobs(
    organization_id: str,
    request: Request,
):
    context = get_job_authorization_context(request)

    if is_global_administrator(context):
        jobs = _job_service.list_all_active_organization_jobs()
    else:
        if organization_id not in context.organization_ids:
            raise HTTPException(
                status_code=403,
                detail="User is not authorized for this organization",
            )
        jobs = _job_service.list_jobs(organization_id)

    return {
        "jobs": [
            job.__dict__
            for job in jobs
        ]
    }


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    job = _job_service.get_job(
        organization_id,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "job": job.__dict__
    }


@router.post("")
async def create_job(
    payload: JobRequest,
    request: Request,
):
    _require_organization_access(
        request,
        payload.organization_id,
    )

    job = Job(
        id="",
        organization_id=payload.organization_id,
        title=payload.title,
        description=payload.description or None,
        employment_type=payload.employment_type or None,
        location=payload.location or None,
        country=payload.country or None,
        status=payload.status,
        number_of_positions=payload.number_of_positions,
        published_at=payload.published_at,
        closing_at=payload.closing_at,
        requisition_number=payload.requisition_number or None,
        employer_name=payload.employer_name or None,
        employer_country=payload.employer_country or None,
        employer_city=payload.employer_city or None,
        trade_skill_category=payload.trade_skill_category or None,
        industry_sector=payload.industry_sector or None,
        gender_requirement=payload.gender_requirement or None,
        minimum_age=payload.minimum_age,
        maximum_age=payload.maximum_age,
        contract_duration=payload.contract_duration or None,
        work_location=payload.work_location or None,
        project_name=payload.project_name or None,
    )

    saved = _job_service.save_job(job)

    return {
        "job": saved.__dict__,
        "message": "Job created",
    }


@router.put("/{job_id}")
async def update_job(
    job_id: str,
    payload: JobRequest,
    request: Request,
):
    _require_organization_access(
        request,
        payload.organization_id,
    )

    existing = _job_service.get_job(
        payload.organization_id,
        job_id,
    )

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    job = Job(
        id=job_id,
        organization_id=payload.organization_id,
        title=payload.title,
        description=payload.description or None,
        employment_type=payload.employment_type or None,
        location=payload.location or None,
        country=payload.country or None,
        status=payload.status,
        number_of_positions=payload.number_of_positions,
        published_at=payload.published_at,
        closing_at=payload.closing_at,
        requisition_number=payload.requisition_number or None,
        employer_name=payload.employer_name or None,
        employer_country=payload.employer_country or None,
        employer_city=payload.employer_city or None,
        trade_skill_category=payload.trade_skill_category or None,
        industry_sector=payload.industry_sector or None,
        gender_requirement=payload.gender_requirement or None,
        minimum_age=payload.minimum_age,
        maximum_age=payload.maximum_age,
        contract_duration=payload.contract_duration or None,
        work_location=payload.work_location or None,
        project_name=payload.project_name or None,
        created_at=existing.created_at,
        updated_at=existing.updated_at,
    )

    saved = _job_service.save_job(job)

    return {
        "job": saved.__dict__,
        "message": "Job updated",
    }
