import base64
import json
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from models.candidate import CandidateProfile
from repositories.application import SqlApplicationRepository
from repositories.candidate import SqlCandidateRepository
from repositories.job import SqlJobRepository
from services.application import ApplicationService
from services.candidate import CandidateService
from services.job import JobService
router = APIRouter(prefix="/api/candidate", tags=["candidate"])
_repository = SqlCandidateRepository()
_service = CandidateService(_repository)
_job_repository = SqlJobRepository()
_job_service = JobService(_job_repository)
_application_repository = SqlApplicationRepository()
_application_service = ApplicationService(_application_repository)
CANDIDATE_GROUP_ID = "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6"
class CandidateApplicationRequest(BaseModel):
    job_id: str
    cover_letter: str | None = None


class CandidateProfileRequest(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    professional_title: str = ""
    summary: str = ""
    location: str = ""
    resume_document_id: str | None = None
def _claim_values(claims: list[dict], claim_type: str) -> set[str]:
    return {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == claim_type and claim.get("val")
    }
def get_candidate_identity(request: Request) -> str:
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    encoded_principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")
    if not principal_id or not encoded_principal:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )
    try:
        padding = "=" * (-len(encoded_principal) % 4)
        principal = json.loads(
            base64.b64decode(
                encoded_principal + padding
            ).decode("utf-8")
        )
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated principal",
        )
    claims = principal.get("claims", [])
    group_ids = _claim_values(claims, "groups")
    token_roles = _claim_values(claims, "roles")
    if CANDIDATE_GROUP_ID not in group_ids and "Candidate" not in token_roles:
        raise HTTPException(
            status_code=403,
            detail="Candidate role is required",
        )
    return principal_id
@router.get("/profile")
async def get_candidate_profile(request: Request):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)
    if profile is None:
        return {
            "profile": None,
            "message": "Candidate profile has not been created yet",
        }
    return {"profile": profile.__dict__}
@router.put("/profile")
async def update_candidate_profile(
    payload: CandidateProfileRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)
    saved = _service.save_profile(
        CandidateProfile(
            user_id=user_id,
            **payload.model_dump(),
        )
    )
    return {
        "profile": saved.__dict__,
        "message": "Candidate profile saved",
    }
@router.get("/jobs")
async def get_candidate_jobs(request: Request):
    get_candidate_identity(request)
    jobs = _job_service.list_published_jobs()
    return {
        "jobs": [job.__dict__ for job in jobs],
    }


@router.get("/applications")
async def get_candidate_applications(request: Request):
    user_id = get_candidate_identity(request)

    candidate_id = _service.get_candidate_id(user_id)

    if candidate_id is None:
        return {
            "applications": [],
            "message": "Candidate profile has not been created yet",
        }

    applications = _application_service.list_candidate_applications(
        candidate_id,
    )

    return {
        "applications": [
            item.__dict__
            for item in applications
        ],
    }


@router.post("/applications")
async def create_candidate_application(
    payload: CandidateApplicationRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)

    candidate_id = _service.get_candidate_id(user_id)

    if candidate_id is None:
        raise HTTPException(
            status_code=400,
            detail="Complete your candidate profile before applying",
        )

    job = _job_service.get_published_job(payload.job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job is no longer available",
        )

    existing = _application_service.list_candidate_applications(
        candidate_id,
    )

    if any(
        application.job_id == payload.job_id
        for application in existing
    ):
        raise HTTPException(
            status_code=409,
            detail="You have already applied for this job",
        )

    try:
        application = _application_service.create_application(
            candidate_id=candidate_id,
            job_id=payload.job_id,
            cover_letter=payload.cover_letter,
        )
    except Exception as exc:
        message = str(exc)

        if "UQ_applications_candidate_job" in message:
            raise HTTPException(
                status_code=409,
                detail="You have already applied for this job",
            )

        raise

    return {
        "application": application.__dict__,
        "message": "Application submitted successfully",
    }
