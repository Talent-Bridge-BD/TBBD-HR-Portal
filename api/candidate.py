import base64
import json
import os
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel, field_validator
from models.candidate import CandidateProfile
from repositories.application import SqlApplicationRepository
from repositories.candidate import SqlCandidateRepository
from repositories.job import SqlJobRepository
from repositories.blob_storage import BlobStorageRepository
from repositories.candidate_document import SqlCandidateDocumentRepository
from repositories.candidate_skill import SqlCandidateSkillRepository
from repositories.candidate_language import SqlCandidateLanguageRepository
from repositories.candidate_experience import SqlCandidateExperienceRepository
from repositories.candidate_preferences import SqlCandidatePreferencesRepository
from services.application import ApplicationService
from services.candidate_document import CandidateDocumentService
from services.candidate_skill import CandidateSkillService
from services.candidate_language import CandidateLanguageService
from services.candidate_experience import CandidateExperienceService
from services.candidate_preferences import CandidatePreferencesService
from services.candidate import CandidateService
from services.job import JobService
from services.local_auth import LOCAL_CANDIDATE_ID, get_request_principal
router = APIRouter(prefix="/api/candidate", tags=["candidate"])
_repository = SqlCandidateRepository()
_service = CandidateService(_repository)
_job_repository = SqlJobRepository()
_job_service = JobService(_job_repository)
_application_repository = SqlApplicationRepository()
_application_service = ApplicationService(_application_repository)
_document_repository = SqlCandidateDocumentRepository()
_blob_repository = BlobStorageRepository()
_document_service = CandidateDocumentService(
    _document_repository,
    _blob_repository,
)

_skill_repository = SqlCandidateSkillRepository()

_skill_service = CandidateSkillService(_skill_repository)

_language_repository = SqlCandidateLanguageRepository()
_language_service = CandidateLanguageService(_language_repository)

_experience_repository = SqlCandidateExperienceRepository()
_experience_service = CandidateExperienceService(_experience_repository)

_preferences_repository = SqlCandidatePreferencesRepository()
_preferences_service = CandidatePreferencesService(_preferences_repository)
CANDIDATE_GROUP_ID = "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6"
class CandidateApplicationRequest(BaseModel):
    job_id: str
    cover_letter: str | None = None


class CandidateSkillRequest(BaseModel):
    skill_name: str
    skill_category: str | None = None
    proficiency: str | None = None

    @field_validator("skill_name")
    @classmethod
    def validate_skill_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Skill name is required")
        if len(value) > 150:
            raise ValueError("Skill name must not exceed 150 characters")
        return value

    @field_validator("skill_category")
    @classmethod
    def validate_skill_category(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("proficiency")
    @classmethod
    def validate_proficiency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower()
        if not value:
            return None

        allowed = {"beginner", "intermediate", "advanced", "expert"}
        if value not in allowed:
            raise ValueError(
                "Proficiency must be beginner, intermediate, advanced, or expert"
            )
        return value


class CandidateLanguageRequest(BaseModel):
    language_name: str
    speaking_proficiency: str | None = None
    reading_proficiency: str | None = None
    writing_proficiency: str | None = None

    @field_validator("language_name")
    @classmethod
    def validate_language_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Language name is required")
        if len(value) > 100:
            raise ValueError("Language name must not exceed 100 characters")
        return value

    @field_validator(
        "speaking_proficiency",
        "reading_proficiency",
        "writing_proficiency",
    )
    @classmethod
    def validate_proficiency(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().lower()
        if not value:
            return None

        allowed = {
            "basic",
            "beginner",
            "elementary",
            "intermediate",
            "advanced",
            "fluent",
            "native",
            "expert",
        }

        if value not in allowed:
            raise ValueError(
                "Language proficiency must be basic, beginner, elementary, "
                "intermediate, advanced, fluent, native, or expert"
            )

        return value


class CandidateExperienceRequest(BaseModel):

    job_title: str
    company: str
    location: str | None = None
    employment_type: str | None = None
    start_date: str
    end_date: str | None = None
    currently_working: bool = False
    description: str | None = None

    @field_validator("job_title")
    @classmethod
    def validate_job_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Job title is required")
        if len(value) > 200:
            raise ValueError("Job title must not exceed 200 characters")
        return value

    @field_validator("company")
    @classmethod
    def validate_company(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Company is required")
        if len(value) > 200:
            raise ValueError("Company must not exceed 200 characters")
        return value

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if len(value) > 200:
            raise ValueError("Location must not exceed 200 characters")
        return value or None

    @field_validator("employment_type")
    @classmethod
    def validate_employment_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        allowed = {"Full-Time", "Part-Time", "Contract", "Temporary"}
        if value not in allowed:
            raise ValueError(
                "Employment type must be Full-Time, Part-Time, Contract, or Temporary"
            )
        return value

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, value: str) -> str:
        from datetime import date

        value = value.strip()
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            raise ValueError("Start date must be a valid date in YYYY-MM-DD format")
        if parsed > date.today():
            raise ValueError("Start date cannot be in the future")
        return value

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value: str | None) -> str | None:
        from datetime import date

        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        try:
            date.fromisoformat(value)
        except ValueError:
            raise ValueError("End date must be a valid date in YYYY-MM-DD format")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    def validate_date_range(self) -> None:
        from datetime import date

        start = date.fromisoformat(self.start_date)

        if self.currently_working:
            if self.end_date is not None:
                raise ValueError(
                    "End date must be empty when currently working is selected"
                )
            return

        if self.end_date is not None:
            end = date.fromisoformat(self.end_date)
            if end < start:
                raise ValueError("End date cannot be before start date")


class CandidatePreferencesRequest(BaseModel):
    preferred_job_title: str | None = None
    preferred_location: str | None = None
    preferred_employment_type: str | None = None
    work_arrangement: str | None = None
    expected_salary: float | None = None
    currency: str | None = None
    availability_notice_period: str | None = None
    open_to_relocation: bool | None = None
    available_for_recruitment: bool = True
    preferred_contact_method: str | None = None

    @field_validator(
        "preferred_job_title",
        "preferred_location",
        "preferred_employment_type",
        "currency",
        "availability_notice_period",
    )
    @classmethod
    def validate_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("work_arrangement")
    @classmethod
    def validate_work_arrangement(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip().lower()

        if value not in {"on_site", "hybrid", "remote"}:
            raise ValueError(
                "Work arrangement must be on_site, hybrid, or remote"
            )

        return value

    @field_validator("preferred_contact_method")
    @classmethod
    def validate_contact_method(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip().lower()

        if value not in {"email", "phone"}:
            raise ValueError(
                "Preferred contact method must be email or phone"
            )

        return value

    @field_validator("expected_salary")
    @classmethod
    def validate_expected_salary(
        cls,
        value: float | None,
    ) -> float | None:
        if value is not None and value < 0:
            raise ValueError(
                "Expected salary cannot be negative"
            )

        return value


class CandidateProfileRequest(BaseModel):
    # Personal information
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""

    # Professional profile
    professional_title: str = ""
    summary: str = ""
    career_level: str = ""
    years_experience: float | None = None

    # Passport / international mobility
    passport_number: str = ""
    passport_country: str = ""
    passport_expiry_date: str | None = None
    passport_status: str = ""
    international_travel_readiness: str = ""

    # Existing document reference
    resume_document_id: str | None = None
    @field_validator("passport_number")
    @classmethod
    def validate_passport_number(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            return value

        import re

        if not re.fullmatch(r"(?:[A-Z]\d{8}|[A-Z]{2}\d{7})", value):
            raise ValueError(
                "Passport number must be in the format "
                "A00000000 or AB0000000"
            )

        return value


def _claim_values(claims: list[dict], claim_type: str) -> set[str]:
    return {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == claim_type and claim.get("val")
    }
def get_candidate_identity(request: Request) -> str:
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

    local_candidate_portal = (
        os.environ.get("TBBD_ENV") == "development"
        and os.environ.get("TBBD_LOCAL_AUTH") == "1"
        and str(principal_id) == "local-administrator-001"
        and request.headers.get("X-TBBD-Local-Portal") == "candidate"
    )

    if local_candidate_portal:
        return LOCAL_CANDIDATE_ID

    if CANDIDATE_GROUP_ID not in group_ids and "Candidate" not in token_roles:
        raise HTTPException(
            status_code=403,
            detail="Candidate role is required",
        )

    return str(principal_id)

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


@router.get("/experience")
def list_candidate_experience(request: Request):

    user_id = get_candidate_identity(request)
    experience = _experience_service.list_experience(user_id)
    return [item.__dict__ for item in experience]


@router.post("/experience", status_code=201)
def create_candidate_experience(
    payload: CandidateExperienceRequest,
    request: Request,
):

    user_id = get_candidate_identity(request)

    try:
        payload.validate_date_range()

        from datetime import date

        experience = _experience_service.create_experience(
            user_id,
            payload.job_title,
            payload.company,
            payload.location,
            payload.employment_type,
            date.fromisoformat(payload.start_date),
            (
                date.fromisoformat(payload.end_date)
                if payload.end_date
                else None
            ),
            payload.currently_working,
            payload.description,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return experience.__dict__


@router.put("/experience/{experience_id}")
def update_candidate_experience(
    experience_id: str,
    payload: CandidateExperienceRequest,
    request: Request,
):

    user_id = get_candidate_identity(request)

    try:
        payload.validate_date_range()

        from datetime import date

        experience = _experience_service.update_experience(
            user_id,
            experience_id,
            payload.job_title,
            payload.company,
            payload.location,
            payload.employment_type,
            date.fromisoformat(payload.start_date),
            (
                date.fromisoformat(payload.end_date)
                if payload.end_date
                else None
            ),
            payload.currently_working,
            payload.description,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if experience is None:
        raise HTTPException(
            status_code=404,
            detail="Experience record not found",
        )

    return experience.__dict__


@router.delete("/experience/{experience_id}", status_code=204)
def delete_candidate_experience(
    experience_id: str,
    request: Request,
):

    user_id = get_candidate_identity(request)

    deleted = _experience_service.delete_experience(
        user_id,
        experience_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Experience record not found",
        )


@router.get("/languages")
def list_candidate_languages(request: Request):
    user_id = get_candidate_identity(request)
    languages = _language_service.list_languages(user_id)
    return [language.__dict__ for language in languages]


@router.post("/languages", status_code=201)
def create_candidate_language(
    payload: CandidateLanguageRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)
    try:
        language = _language_service.create_language(
            user_id,
            payload.language_name,
            payload.speaking_proficiency,
            payload.reading_proficiency,
            payload.writing_proficiency,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return language.__dict__


@router.put("/languages/{language_id}")
def update_candidate_language(
    language_id: str,
    payload: CandidateLanguageRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)
    try:
        language = _language_service.update_language(
            user_id,
            language_id,
            payload.language_name,
            payload.speaking_proficiency,
            payload.reading_proficiency,
            payload.writing_proficiency,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if language is None:
        raise HTTPException(status_code=404, detail="Language not found")

    return language.__dict__


@router.delete("/languages/{language_id}", status_code=204)
def delete_candidate_language(
    language_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)
    deleted = _language_service.delete_language(
        user_id,
        language_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Language not found")


@router.get("/skills")
def list_candidate_skills(request: Request):
    user_id = get_candidate_identity(request)
    skills = _skill_service.list_skills(user_id)
    return [skill.__dict__ for skill in skills]


@router.post("/skills", status_code=201)
def create_candidate_skill(
    payload: CandidateSkillRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)

    try:
        skill = _skill_service.create_skill(
            user_id,
            payload.skill_name,
            payload.skill_category,
            payload.proficiency,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return skill.__dict__


@router.put("/skills/{skill_id}")
def update_candidate_skill(
    skill_id: str,
    payload: CandidateSkillRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)

    try:
        skill = _skill_service.update_skill(
            user_id,
            skill_id,
            payload.skill_name,
            payload.skill_category,
            payload.proficiency,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    return skill.__dict__


@router.delete("/skills/{skill_id}", status_code=204)
def delete_candidate_skill(
    skill_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)

    deleted = _skill_service.delete_skill(
        user_id,
        skill_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Skill not found")


@router.get("/preferences")
def get_candidate_preferences(request: Request):
    user_id = get_candidate_identity(request)

    preferences = _preferences_service.get_preferences(user_id)

    if preferences is None:
        return {
            "preferences": None,
        }

    return {
        "preferences": preferences.__dict__,
    }


@router.put("/preferences")
def save_candidate_preferences(
    payload: CandidatePreferencesRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)

    try:
        preferences = _preferences_service.save_preferences(
            candidate_id=user_id,
            preferred_job_title=payload.preferred_job_title,
            preferred_location=payload.preferred_location,
            preferred_employment_type=payload.preferred_employment_type,
            work_arrangement=payload.work_arrangement,
            expected_salary=payload.expected_salary,
            currency=payload.currency,
            availability_notice_period=payload.availability_notice_period,
            open_to_relocation=payload.open_to_relocation,
            available_for_recruitment=payload.available_for_recruitment,
            preferred_contact_method=payload.preferred_contact_method,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "preferences": preferences.__dict__,
        "message": "Candidate preferences saved",
    }


@router.get("/documents")
async def get_candidate_documents(request: Request):
    user_id = get_candidate_identity(request)
    candidate_id = _service.get_candidate_id(user_id)

    if candidate_id is None:
        return {
            "documents": [],
            "message": "Candidate profile has not been created yet",
        }

    documents = _document_service.list_documents(candidate_id)

    return {
        "documents": [document.__dict__ for document in documents]
    }


@router.post("/documents")
async def upload_candidate_document(
    request: Request,
    document_type: str,
    file: UploadFile = File(...),
):
    user_id = get_candidate_identity(request)
    candidate_id = _service.get_candidate_id(user_id)

    if candidate_id is None:
        raise HTTPException(
            status_code=400,
            detail="Complete your candidate profile before uploading documents",
        )

    if document_type not in {"profile_photo", "passport", "resume"}:
        raise HTTPException(
            status_code=400,
            detail="Document type must be profile_photo, passport, or resume",
        )

    max_upload_bytes = CandidateDocumentService.MAX_FILE_SIZE + 1
    file_bytes = await file.read(max_upload_bytes)

    try:
        document = _document_service.upload_document(
            candidate_id=candidate_id,
            document_type=document_type,
            file_name=file.filename or "document",
            content_type=file.content_type or "",
            file_bytes=file_bytes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "document": document.__dict__,
        "message": "Document uploaded successfully",
    }


@router.get("/documents/{document_id}")
async def download_candidate_document(
    document_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)
    candidate_id = _service.get_candidate_id(user_id)

    if candidate_id is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found",
        )

    document = _document_repository.get_document(
        candidate_id,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        file_bytes = _blob_repository.download(document.blob_name)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Document file could not be retrieved",
        )

    from fastapi.responses import Response

    return Response(
        content=file_bytes,
        media_type=document.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{document.file_name}"'
            )
        },
    )


@router.delete("/documents/{document_id}")
async def delete_candidate_document(
    document_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)
    candidate_id = _service.get_candidate_id(user_id)

    if candidate_id is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found",
        )

    try:
        document = _document_service.delete_document(
            candidate_id,
            document_id,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document could not be deleted",
        )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "document": document.__dict__,
        "message": "Document deleted successfully",
    }
