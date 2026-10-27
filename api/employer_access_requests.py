import re
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from api.administrator_organizations import require_admin
from repositories.employer_access_requests import (
    SqlEmployerAccessRequestRepository,
)
from services.local_auth import get_request_principal


router = APIRouter(
    tags=["Employer Access Requests"],
)

_repository = SqlEmployerAccessRequestRepository()


class EmployerAccessRequestCreate(BaseModel):
    contact_name: str = Field(min_length=2, max_length=160)
    work_email: str = Field(min_length=5, max_length=320)
    organization_name: str = Field(min_length=2, max_length=200)
    website: str = Field(min_length=4, max_length=500)
    business_details: str = Field(min_length=10, max_length=2000)
    access_reason: str = Field(min_length=10, max_length=2000)


class EmployerAccessRequestReview(BaseModel):
    status: str
    review_notes: str | None = Field(default=None, max_length=2000)


def _validate_submission(payload: EmployerAccessRequestCreate) -> dict:
    data = payload.model_dump()
    for key, value in data.items():
        data[key] = value.strip()
        if not data[key]:
            raise HTTPException(
                status_code=422,
                detail=f"{key} must not be blank",
            )

    email = data["work_email"]
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid work email")
    data["work_email"] = email.casefold()

    website = data["website"]
    parsed = urlsplit(
        website if "://" in website else f"https://{website}"
    )
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or "." not in parsed.hostname
        or any(character.isspace() for character in website)
    ):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid organization website",
        )
    data["website"] = parsed.geturl()

    return data


@router.post("/api/employer-access-requests", status_code=201)
def submit_employer_access_request(
    payload: EmployerAccessRequestCreate,
):
    data = _validate_submission(payload)
    try:
        item = _repository.create_request(data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "request_id": item["id"],
        "status": item["status"],
        "message": (
            "Your request has been received for review. "
            "Submitting a request does not create an account or grant portal access."
        ),
    }


@router.get("/api/administrator/employer-access-requests")
def list_employer_access_requests(
    request: Request,
    status: str | None = Query(default="pending"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    require_admin(request)

    if status not in {None, "pending", "approved", "rejected"}:
        raise HTTPException(status_code=422, detail="Invalid request status")

    try:
        items = _repository.list_requests(
            status=status,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {"items": items, "limit": limit, "offset": offset}


@router.post(
    "/api/administrator/employer-access-requests/{request_id}/review"
)
def review_employer_access_request(
    request_id: str,
    payload: EmployerAccessRequestReview,
    request: Request,
):
    require_admin(request)

    try:
        parsed_id = str(UUID(request_id))
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(
            status_code=422,
            detail="Invalid request ID",
        ) from exc

    if payload.status not in {"approved", "rejected"}:
        raise HTTPException(
            status_code=422,
            detail="Review status must be approved or rejected",
        )

    principal = get_request_principal(request)
    reviewer = str((principal or {}).get("id") or "").strip()
    if not reviewer:
        raise HTTPException(
            status_code=401,
            detail="Reviewer identity is required",
        )

    try:
        item = _repository.review_request(
            parsed_id,
            status=payload.status,
            reviewed_by=reviewer,
            review_notes=payload.review_notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if item is None:
        raise HTTPException(
            status_code=409,
            detail="Request was not found or has already been reviewed",
        )

    return {"item": item}
