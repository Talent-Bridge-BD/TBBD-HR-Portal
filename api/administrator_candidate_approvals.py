from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from api.administrator_organizations import require_admin
from repositories.candidate_approvals import SqlCandidateApprovalRepository
from repositories.candidate import SqlCandidateRepository
from repositories.candidate_document import SqlCandidateDocumentRepository
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/administrator/candidate-approvals",
    tags=["administrator candidate approvals"],
)

_repository = SqlCandidateApprovalRepository()
_candidate_repository = SqlCandidateRepository()
_document_repository = SqlCandidateDocumentRepository()


def _profile_completion_errors(entra_object_id: str) -> list[str]:
    candidate_id = _candidate_repository.get_candidate_id(entra_object_id)
    if not candidate_id:
        raise RuntimeError("Candidate profile could not be verified")

    profile = _candidate_repository.get_profile(entra_object_id)
    if not profile:
        raise RuntimeError("Candidate profile could not be verified")

    documents = _document_repository.list_documents(candidate_id)
    document_types = {document.document_type for document in documents}

    required_values = {
        "First name": profile.first_name,
        "Email": profile.email,
        "Phone": profile.phone,
        "Location": profile.location,
        "Professional title": profile.professional_title,
        "Career level": profile.career_level,
        "Passport country": profile.passport_country,
        "Passport expiry date": profile.passport_expiry_date,
        "Passport status": profile.passport_status,
        "International travel readiness": profile.international_travel_readiness,
    }

    missing = [
        label for label, value in required_values.items()
        if not str(value or "").strip()
    ]

    if profile.years_experience is None or str(profile.years_experience).strip() == "":
        missing.append("Years of experience")

    for document_type, label in (
        ("resume", "Resume"),
        ("passport", "Passport document"),
        ("profile_photo", "Profile photo"),
    ):
        if document_type not in document_types:
            missing.append(label)

    return missing


class CandidateReviewRequest(BaseModel):
    status: str
    approval_notes: str | None = Field(default=None, max_length=2000)


class BulkCandidateApprovalRequest(BaseModel):
    entra_object_ids: list[str]
    approval_notes: str | None = Field(default=None, max_length=2000)


def _reviewer_id(request: Request) -> str:
    principal = get_request_principal(request)
    reviewer = str((principal or {}).get("id") or "").strip()
    if not reviewer:
        raise HTTPException(
            status_code=401,
            detail="Authenticated reviewer required",
        )
    return reviewer


@router.get("")
def list_candidate_approvals(
    request: Request,
    status: str | None = None,
    search: str | None = None,
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    require_admin(request)

    if status is not None and status not in {
        "pending", "approved", "rejected"
    }:
        raise HTTPException(status_code=422, detail="Invalid approval status")

    try:
        rows = _repository.list_approvals(
            status=status,
            search=search,
            limit=limit + 1,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    has_more = len(rows) > limit
    return {
        "items": rows[:limit],
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }


@router.post("/{entra_object_id}/review")
def review_candidate(
    entra_object_id: str,
    payload: CandidateReviewRequest,
    request: Request,
):
    require_admin(request)

    if payload.status not in {"approved", "rejected"}:
        raise HTTPException(
            status_code=422,
            detail="Review status must be approved or rejected",
        )

    if payload.status == "approved":
        try:
            missing_items = _profile_completion_errors(entra_object_id)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Candidate profile verification failed; approval was not changed",
            ) from exc

        if missing_items:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Candidate profile is incomplete",
                    "missing_items": missing_items,
                },
            )
    try:
        result = _repository.review_candidate(
            entra_object_id,
            status=payload.status,
            reviewed_by=_reviewer_id(request),
            approval_notes=payload.approval_notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(
            status_code=409,
            detail="Candidate was not found or is no longer pending",
        )

    return {"item": result, "status": "updated"}


@router.post("/bulk-approve")
def bulk_approve_candidates(
    payload: BulkCandidateApprovalRequest,
    request: Request,
):
    require_admin(request)

    ids = list(dict.fromkeys(
        value.strip()
        for value in payload.entra_object_ids
        if isinstance(value, str) and value.strip()
    ))

    if not ids or len(ids) > 100:
        raise HTTPException(
            status_code=422,
            detail="Provide between 1 and 100 candidate IDs",
        )

    reviewer = _reviewer_id(request)
    results = []

    for entra_object_id in ids:
        try:
            missing_items = _profile_completion_errors(entra_object_id)
        except Exception:
            results.append({
                "entra_object_id": entra_object_id,
                "status": "error",
                "detail": "Candidate profile verification failed; not approved",
            })
            continue

        if missing_items:
            results.append({
                "entra_object_id": entra_object_id,
                "status": "error",
                "detail": "Candidate profile is incomplete",
                "missing_items": missing_items,
            })
            continue

        try:
            result = _repository.review_candidate(
                entra_object_id,
                status="approved",
                reviewed_by=reviewer,
                approval_notes=payload.approval_notes,
            )
        except ValueError as exc:
            results.append({
                "entra_object_id": entra_object_id,
                "status": "error",
                "detail": str(exc),
            })
            continue

        results.append({
            "entra_object_id": entra_object_id,
            "status": "approved" if result else "skipped",
            "item": result,
        })

    return {
        "results": results,
        "approved_count": sum(
            item["status"] == "approved" for item in results
        ),
        "skipped_count": sum(
            item["status"] == "skipped" for item in results
        ),
        "error_count": sum(
            item["status"] == "error" for item in results
        ),
    }
