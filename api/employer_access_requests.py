import re
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
    company_name: str = Field(min_length=2, max_length=200)
    representative_name: str = Field(min_length=2, max_length=200)
    email: str = Field(min_length=5, max_length=320)
    phone: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=150)
    requested_roles: str | None = Field(default=None, max_length=1000)
    requirements: str | None = Field(default=None, max_length=10000)


class EmployerAccessRequestReview(BaseModel):
    status: str
    review_notes: str | None = Field(default=None, max_length=2000)


def _validate_submission(payload: EmployerAccessRequestCreate) -> dict:
    data = payload.model_dump()

    for key in ("company_name", "representative_name", "email"):
        value = (data.get(key) or "").strip()
        if not value:
            raise HTTPException(
                status_code=422,
                detail=f"{key} must not be blank",
            )
        data[key] = value

    for key in ("phone", "country", "industry", "requested_roles", "requirements"):
        data[key] = (data.get(key) or "").strip() or None

    email = data["email"]
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid business email")
    data["email"] = email.casefold()

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
