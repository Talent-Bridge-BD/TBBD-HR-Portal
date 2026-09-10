import base64
import json

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from models.candidate import CandidateProfile
from models.candidate_experience import CandidateExperience
from models.candidate_education import CandidateEducation
from models.candidate_skill import CandidateSkill
from models.candidate_certification import CandidateCertification
from models.candidate_document import CandidateDocument
from models.candidate_preferences import CandidatePreferences
from repositories.candidate import SqlCandidateRepository
from repositories.candidate_experience import SqlCandidateExperienceRepository
from repositories.candidate_education import SqlCandidateEducationRepository
from repositories.candidate_skill import SqlCandidateSkillRepository
from repositories.candidate_certification import SqlCandidateCertificationRepository
from repositories.candidate_document import SqlCandidateDocumentRepository
from repositories.candidate_preferences import SqlCandidatePreferencesRepository
from repositories.job import SqlJobRepository
from services.candidate import CandidateService
from services.candidate_experience import CandidateExperienceService
from services.candidate_education import CandidateEducationService
from services.candidate_skill import CandidateSkillService
from services.candidate_certification import CandidateCertificationService
from services.candidate_document import CandidateDocumentService
from services.candidate_document_storage import CandidateDocumentStorageService
from services.candidate_preferences import CandidatePreferencesService
from services.job import JobService


router = APIRouter(prefix="/api/candidate", tags=["candidate"])

_repository = SqlCandidateRepository()
_service = CandidateService(_repository)
_experience_repository = SqlCandidateExperienceRepository()
_experience_service = CandidateExperienceService(_experience_repository)
_education_repository = SqlCandidateEducationRepository()
_education_service = CandidateEducationService(_education_repository)
_skill_repository = SqlCandidateSkillRepository()
_skill_service = CandidateSkillService(_skill_repository)
_certification_repository = SqlCandidateCertificationRepository()
_certification_service = CandidateCertificationService(_certification_repository)
_job_repository = SqlJobRepository()
_job_service = JobService(_job_repository)

_document_repository = SqlCandidateDocumentRepository()

_document_storage = CandidateDocumentStorageService()

_document_service = CandidateDocumentService(
    _document_repository,
    _document_storage,
)
_preferences_repository = SqlCandidatePreferencesRepository()
_preferences_service = CandidatePreferencesService(_preferences_repository)

CANDIDATE_GROUP_ID = "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6"


class CandidateProfileRequest(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    professional_title: str = ""
    summary: str = ""
    location: str = ""
    country: str = ""
    years_experience: float | None = None
    current_company: str = ""
    resume_document_id: str | None = None

    @field_validator(
        "first_name",
        "last_name",
        "phone",
        "professional_title",
        "summary",
        "location",
        "country",
        "current_company",
    )
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if not value or "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("A valid email address is required")
        return value

    @field_validator("years_experience")
    @classmethod
    def validate_years_experience(cls, value: float | None) -> float | None:
        if value is not None and (value < 0 or value > 80):
            raise ValueError("Years of experience must be between 0 and 80")
        return value


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
            raise ValueError("Expected salary cannot be negative")
        return value


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
        return value

    @field_validator("skill_category", "proficiency")
    @classmethod
    def validate_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class CandidateEducationRequest(BaseModel):
    degree_qualification: str
    institution: str
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None

    @field_validator("degree_qualification", "institution")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError(
                "Degree/qualification and institution are required"
            )
        return value

    @field_validator(
        "field_of_study",
        "description",
    )
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        try:
            from datetime import date
            date.fromisoformat(value)
        except ValueError:
            raise ValueError("Dates must use YYYY-MM-DD format")
        return value

    @field_validator("end_date")
    @classmethod
    def validate_end_date(
        cls,
        value: str | None,
        info,
    ) -> str | None:
        if value is None:
            return None

        start_date = info.data.get("start_date")

        if (
            start_date is not None
            and value < start_date
        ):
            raise ValueError(
                "End date cannot be earlier than start date"
            )

        return value


class CandidateCertificationRequest(BaseModel):
    certification_name: str
    issuing_organization: str
    issue_date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None

    @field_validator("certification_name", "issuing_organization")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError(
                "Certification name and issuing organization are required"
            )
        return value

    @field_validator("credential_id")
    @classmethod
    def validate_credential_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("issue_date", "expiry_date")
    @classmethod
    def validate_date_format(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        try:
            from datetime import date
            date.fromisoformat(value)
        except ValueError:
            raise ValueError("Dates must use YYYY-MM-DD format")
        return value

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(
        cls,
        value: str | None,
        info,
    ) -> str | None:
        if value is None:
            return None

        issue_date = info.data.get("issue_date")

        if (
            issue_date is not None
            and value < issue_date
        ):
            raise ValueError(
                "Expiry date cannot be earlier than issue date"
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

    @field_validator("job_title", "company")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Job title and company are required")
        return value

    @field_validator(
        "location",
        "employment_type",
        "description",
    )
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        try:
            from datetime import date
            date.fromisoformat(value)
        except ValueError:
            raise ValueError("Dates must use YYYY-MM-DD format")
        return value

    @field_validator("end_date")
    @classmethod
    def validate_end_date(
        cls,
        value: str | None,
        info,
    ) -> str | None:
        if value is None:
            return None

        start_date = info.data.get("start_date")
        if start_date is not None and value < start_date:
            raise ValueError("End date cannot be earlier than start date")

        return value

    @field_validator("currently_working")
    @classmethod
    def validate_current_status(
        cls,
        value: bool,
        info,
    ) -> bool:
        end_date = info.data.get("end_date")

        if value and end_date is not None:
            raise ValueError(
                "Currently working experience cannot have an end date"
            )

        if not value and end_date is None:
            raise ValueError(
                "End date is required when currently working is false"
            )

        return value


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


@router.get("/experience")
async def get_candidate_experience(request: Request):
    user_id = get_candidate_identity(request)

    profile = _service.get_profile(user_id)
    if profile is None:
        return {
            "experience": [],
            "message": "Candidate profile has not been created yet",
        }

    experiences = _experience_service.list_experience(profile.user_id)

    return {
        "experience": [
            experience.__dict__
            for experience in experiences
        ],
    }


@router.post("/experience")
async def create_candidate_experience(
    payload: CandidateExperienceRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)

    profile = _service.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    experience = _experience_service.create_experience(
        candidate_id=profile.user_id,
        job_title=payload.job_title,
        company=payload.company,
        location=payload.location,
        employment_type=payload.employment_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        currently_working=payload.currently_working,
        description=payload.description,
    )

    return {
        "experience": experience.__dict__,
        "message": "Work experience added",
    }


@router.put("/experience/{experience_id}")
async def update_candidate_experience(
    experience_id: str,
    payload: CandidateExperienceRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)

    profile = _service.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    experience = _experience_service.update_experience(
        candidate_id=profile.user_id,
        experience_id=experience_id,
        job_title=payload.job_title,
        company=payload.company,
        location=payload.location,
        employment_type=payload.employment_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        currently_working=payload.currently_working,
        description=payload.description,
    )

    if experience is None:
        raise HTTPException(
            status_code=404,
            detail="Work experience not found",
        )

    return {
        "experience": experience.__dict__,
        "message": "Work experience updated",
    }


@router.delete("/experience/{experience_id}")
async def delete_candidate_experience(
    experience_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)

    profile = _service.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    deleted = _experience_service.delete_experience(
        candidate_id=profile.user_id,
        experience_id=experience_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Work experience not found",
        )

    return {
        "message": "Work experience deleted",
    }

@router.get("/education")
async def get_candidate_education(request: Request):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        return {
            "education": [],
            "message": "Candidate profile has not been created yet",
        }

    education = _education_service.list_education(profile.user_id)

    return {
        "education": [
            item.__dict__
            for item in education
        ],
    }


@router.post("/education")
async def create_candidate_education(
    payload: CandidateEducationRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    education = _education_service.create_education(
        candidate_id=profile.user_id,
        degree_qualification=payload.degree_qualification,
        institution=payload.institution,
        field_of_study=payload.field_of_study,
        start_date=payload.start_date,
        end_date=payload.end_date,
        description=payload.description,
    )

    return {
        "education": education.__dict__,
        "message": "Education added",
    }


@router.put("/education/{education_id}")
async def update_candidate_education(
    education_id: str,
    payload: CandidateEducationRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    education = _education_service.update_education(
        candidate_id=profile.user_id,
        education_id=education_id,
        degree_qualification=payload.degree_qualification,
        institution=payload.institution,
        field_of_study=payload.field_of_study,
        start_date=payload.start_date,
        end_date=payload.end_date,
        description=payload.description,
    )

    if education is None:
        raise HTTPException(
            status_code=404,
            detail="Education record not found",
        )

    return {
        "education": education.__dict__,
        "message": "Education updated",
    }


@router.delete("/education/{education_id}")
async def delete_candidate_education(
    education_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    deleted = _education_service.delete_education(
        candidate_id=profile.user_id,
        education_id=education_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Education record not found",
        )

    return {
        "message": "Education deleted",
    }


@router.get("/skills")
async def get_candidate_skills(request: Request):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        return {
            "skills": [],
            "message": "Candidate profile has not been created yet",
        }

    skills = _skill_service.list_skills(profile.user_id)

    return {
        "skills": [
            skill.__dict__
            for skill in skills
        ],
    }


@router.post("/skills")
async def create_candidate_skill(
    payload: CandidateSkillRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    skill = _skill_service.create_skill(
        candidate_id=profile.user_id,
        skill_name=payload.skill_name,
        skill_category=payload.skill_category,
        proficiency=payload.proficiency,
    )

    return {
        "skill": skill.__dict__,
        "message": "Skill added",
    }


@router.put("/skills/{skill_id}")
async def update_candidate_skill(
    skill_id: str,
    payload: CandidateSkillRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    skill = _skill_service.update_skill(
        candidate_id=profile.user_id,
        skill_id=skill_id,
        skill_name=payload.skill_name,
        skill_category=payload.skill_category,
        proficiency=payload.proficiency,
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return {
        "skill": skill.__dict__,
        "message": "Skill updated",
    }


@router.delete("/skills/{skill_id}")
async def delete_candidate_skill(
    skill_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    deleted = _skill_service.delete_skill(
        candidate_id=profile.user_id,
        skill_id=skill_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return {
        "message": "Skill deleted",
    }


@router.get("/certifications")
async def get_candidate_certifications(request: Request):

    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        return {
            "certifications": [],
            "message": "Candidate profile has not been created yet",
        }

    certifications = _certification_service.list_certifications(
        profile.user_id
    )

    return {
        "certifications": [
            certification.__dict__
            for certification in certifications
        ],
    }


@router.post("/certifications")
async def create_candidate_certification(
    payload: CandidateCertificationRequest,
    request: Request,
):

    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    certification = _certification_service.create_certification(
        candidate_id=profile.user_id,
        certification_name=payload.certification_name,
        issuing_organization=payload.issuing_organization,
        issue_date=payload.issue_date,
        expiry_date=payload.expiry_date,
        credential_id=payload.credential_id,
    )

    if certification is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    return {
        "certification": certification.__dict__,
        "message": "Certification added",
    }


@router.put("/certifications/{certification_id}")
async def update_candidate_certification(
    certification_id: str,
    payload: CandidateCertificationRequest,
    request: Request,
):

    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    certification = _certification_service.update_certification(
        candidate_id=profile.user_id,
        certification_id=certification_id,
        certification_name=payload.certification_name,
        issuing_organization=payload.issuing_organization,
        issue_date=payload.issue_date,
        expiry_date=payload.expiry_date,
        credential_id=payload.credential_id,
    )

    if certification is None:
        raise HTTPException(
            status_code=404,
            detail="Certification not found",
        )

    return {
        "certification": certification.__dict__,
        "message": "Certification updated",
    }


@router.delete("/certifications/{certification_id}")
async def delete_candidate_certification(
    certification_id: str,
    request: Request,
):

    user_id = get_candidate_identity(request)
    profile = _service.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    deleted = _certification_service.delete_certification(
        candidate_id=profile.user_id,
        certification_id=certification_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Certification not found",
        )

    return {
        "message": "Certification deleted",
    }


@router.get("/documents")
async def list_candidate_documents(request: Request):
    user_id = get_candidate_identity(request)
    documents = _document_service.list_documents(user_id)

    return {
        "documents": [document.__dict__ for document in documents],
    }


@router.post("/documents")
async def upload_candidate_document(
    request: Request,
    document_type: str = Form(...),
    file: UploadFile = File(...),
):
    user_id = get_candidate_identity(request)

    allowed_document_types = {
        "resume",
        "certificate",
        "identification",
        "identity",
        "passport",
        "cover_letter",
        "application_document",
        "other",
    }

    document_type = document_type.strip().lower()

    if document_type not in allowed_document_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported document type",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required",
        )

    content = await file.read()

    try:
        document = _document_service.create_document(
            user_id=user_id,
            document_type=document_type,
            file_name=file.filename,
            content_type=file.content_type or "",
            content=content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "document": document.__dict__,
        "message": "Document uploaded",
    }


@router.get("/documents/{document_id}/content")
async def download_candidate_document(
    document_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)

    try:
        result = _document_service.download_document(
            user_id=user_id,
            document_id=document_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail="Document content not found",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    document, content = result

    return StreamingResponse(
        iter([content]),
        media_type=document.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{document.file_name}"'
            )
        },
    )


@router.get("/documents/{document_id}")
async def get_candidate_document(
    document_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)
    document = _document_service.get_document(
        user_id=user_id,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "document": document.__dict__,
    }


@router.delete("/documents/{document_id}")
async def delete_candidate_document(
    document_id: str,
    request: Request,
):
    user_id = get_candidate_identity(request)

    deleted = _document_service.delete_document(
        user_id=user_id,
        document_id=document_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "message": "Document deleted",
    }


@router.get("/preferences")
async def get_candidate_preferences(request: Request):
    user_id = get_candidate_identity(request)

    profile = _service.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    preferences = _preferences_service.get_preferences(
        candidate_id=profile.user_id,
    )

    if preferences is None:
        return {
            "preferences": None,
        }

    return {
        "preferences": preferences.__dict__,
    }


@router.put("/preferences")
async def save_candidate_preferences(
    payload: CandidatePreferencesRequest,
    request: Request,
):
    user_id = get_candidate_identity(request)

    profile = _service.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile has not been created yet",
        )

    try:
        preferences = _preferences_service.save_preferences(
            candidate_id=profile.user_id,
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
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "preferences": preferences.__dict__,
        "message": "Candidate preferences saved",
    }


@router.get("/jobs")
async def get_candidate_jobs(request: Request):
    get_candidate_identity(request)

    jobs = _job_service.list_published_jobs()

    return {
        "jobs": [job.__dict__ for job in jobs],
    }

