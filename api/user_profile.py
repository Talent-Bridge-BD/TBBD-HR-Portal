import base64
import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from models.user_profile import UserProfile
from repositories.user_profile import SqlUserProfileRepository
from services.user_profile import UserProfileService


router = APIRouter(prefix="/api/profile", tags=["profile"])

_profile_repository = SqlUserProfileRepository()
_profile_service = UserProfileService(_profile_repository)


class UserProfileRequest(BaseModel):
    full_name: str = ""
    phone: str = ""
    organization_email: str = ""


def get_authenticated_user_id(request: Request) -> str:
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    encoded_principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not principal_id or not encoded_principal:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    try:
        padding = "=" * (-len(encoded_principal) % 4)
        base64.b64decode(
            encoded_principal + padding
        ).decode("utf-8")
        json.loads(
            base64.b64decode(
                encoded_principal + padding
            ).decode("utf-8")
        )
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated principal",
        )

    return principal_id


@router.get("")
async def get_profile(request: Request):
    user_id = get_authenticated_user_id(request)
    profile = _profile_service.get_profile(user_id)

    if profile is None:
        return {
            "profile": {
                "user_id": user_id,
                "full_name": "",
                "phone": "",
                "organization_email": "",
            }
        }

    return {
        "profile": profile.__dict__
    }


@router.put("")
async def update_profile(
    payload: UserProfileRequest,
    request: Request,
):
    user_id = get_authenticated_user_id(request)

    profile = UserProfile(
        user_id=user_id,
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip(),
        organization_email=payload.organization_email.strip(),
    )

    saved = _profile_service.save_profile(profile)

    return {
        "profile": saved.__dict__,
        "message": "Profile updated",
    }
