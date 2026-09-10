import base64
import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from models.candidate import CandidateProfile
from repositories.candidate import SqlCandidateRepository
from services.candidate import CandidateService


router = APIRouter(prefix="/api/candidate", tags=["candidate"])

_repository = SqlCandidateRepository()
_service = CandidateService(_repository)

CANDIDATE_GROUP_ID = "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6"


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
