from decimal import Decimal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from models.job_compensation import JobCompensation
from repositories.job import SqlJobRepository
from repositories.job_compensation import SqlJobCompensationRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    AUTHORIZATION_GROUPS,
    build_authorization_context,
    is_global_administrator,
)
from services.job import JobService
from services.job_compensation import JobCompensationService


router = APIRouter(
    prefix="/api/jobs/{job_id}/compensation",
    tags=["job-compensation"],
)

_job_repository = SqlJobRepository()
_job_service = JobService(_job_repository)

_compensation_repository = SqlJobCompensationRepository()
_compensation_service = JobCompensationService(
    _compensation_repository
)

_organization_repository = SqlOrganizationRepository()


class JobCompensationRequest(BaseModel):
    organization_id: str
    salary_currency: str = ""
    basic_salary: Decimal | None = None
    overtime_rate: Decimal | None = None
    food_provided: bool = False
    accommodation_provided: bool = False
    transportation_provided: bool = False
    medical_coverage: bool = False
    air_ticket_provided: bool = False
    leave_entitlement: str = ""
    other_benefits: str = ""


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


def get_job_compensation_authorization_context(
    request: Request,
):
    principal_id = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL-ID"
    )
    encoded_principal = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL"
    )

    if not principal_id or not encoded_principal:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    import base64
    import json

    try:
        padding = "=" * (-len(encoded_principal) % 4)
        principal = json.loads(
            base64.b64decode(
                encoded_principal + padding
            ).decode("utf-8")
        )
    except (
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated principal",
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


def _require_job_access(
    request: Request,
    organization_id: str,
    job_id: str,
):
    context = get_job_compensation_authorization_context(request)

    if is_global_administrator(context):
        return context

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
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

    return context, job


@router.get("")
async def get_job_compensation(
    job_id: str,
    organization_id: str,
    request: Request,
):
    _require_job_access(
        request,
        organization_id,
        job_id,
    )

    compensation = _compensation_service.get_by_job_id(
        job_id
    )

    if compensation is None:
        return {
            "compensation": None,
        }

    return {
        "compensation": compensation.__dict__,
    }


@router.put("")
async def save_job_compensation(
    job_id: str,
    payload: JobCompensationRequest,
    request: Request,
):
    _require_job_access(
        request,
        payload.organization_id,
        job_id,
    )

    compensation = _compensation_service.save(
        JobCompensation(
            id="",
            job_id=job_id,
            salary_currency=payload.salary_currency or None,
            basic_salary=payload.basic_salary,
            overtime_rate=payload.overtime_rate,
            food_provided=payload.food_provided,
            accommodation_provided=payload.accommodation_provided,
            transportation_provided=payload.transportation_provided,
            medical_coverage=payload.medical_coverage,
            air_ticket_provided=payload.air_ticket_provided,
            leave_entitlement=payload.leave_entitlement or None,
            other_benefits=payload.other_benefits or None,
        )
    )

    return {
        "compensation": compensation.__dict__,
        "message": "Job compensation saved",
    }
