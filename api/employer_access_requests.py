from __future__ import annotations

import html
import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.administrator_organizations import require_admin
from repositories.employer_access_requests import (
    EmployerAccessRequestRepository,
)

from services.email_service import EmailService
from repositories.administrator_notifications import AdministratorNotificationRepository

router = APIRouter(
    prefix="/api/employer-access-requests",
    tags=["employer-access-requests"],
)

public_router = APIRouter(
    prefix="/api/public/employer-access-requests",
    tags=["public-employer-access-requests"],
)


_repository = EmployerAccessRequestRepository()
_delivery_log_repository = AdministratorNotificationRepository()


class EmployerAccessRequestCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    company_name: str = Field(min_length=2, max_length=200)
    representative_name: str = Field(min_length=2, max_length=200)
    email: str = Field(min_length=5, max_length=320)
    phone: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=150)
    requested_roles: str | None = Field(default=None, max_length=1000)
    requirements: str | None = Field(default=None, max_length=10000)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Enter a valid email address")
        return value


class EmployerAccessRequestReview(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    status: Literal["Approved", "Rejected"]
    review_notes: str | None = Field(default=None, max_length=2000)


@public_router.post("", status_code=201)
def submit_employer_access_request(
    payload: EmployerAccessRequestCreate,
):
    """Publicly submit a request; this does not grant portal access."""
    try:
        request_record = _repository.create_request(
            **payload.model_dump()
        )
    except Exception:
        # Avoid returning database details to anonymous callers.
        raise HTTPException(
            status_code=503,
            detail="The request could not be saved right now. Please try again later.",
        ) from None

    return {
        "message": "Your employer access request was submitted for review.",
        "request": {
            "id": request_record["id"],
            "status": request_record["status"],
            "created_at": request_record["created_at"],
        },
    }


@router.get("")
def list_employer_access_requests(
    request: Request,
    status: Literal["Pending", "Approved", "Rejected"] | None = Query(
        default=None
    ),
    limit: int = Query(default=100, ge=1, le=500),
):
    """Only global Administrators may list requests."""
    require_admin(request)

    try:
        records = _repository.list_requests(status=status, limit=limit)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Employer access requests are temporarily unavailable.",
        ) from None

    return {"requests": records}


@router.patch("/{request_id}/review")
def review_employer_access_request(
    request: Request,
    request_id: str,
    payload: EmployerAccessRequestReview,
):
    """Only global Administrators may approve or reject a request."""
    context = require_admin(request)

    principal = None
    try:
        from services.local_auth import get_request_principal

        principal = get_request_principal(request)
    except Exception:
        principal = None

    reviewer_id = (
        str(principal.get("id"))
        if principal and principal.get("id")
        else None
    )
    reviewer_email = (
        str(principal.get("email"))
        if principal and principal.get("email")
        else None
    )

    if not reviewer_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated Administrator identity required",
        )

    try:
        record = _repository.review_request(
            request_id,
            status=payload.status,
            reviewed_by=reviewer_email or reviewer_id,
            review_notes=payload.review_notes,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from None
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The request could not be reviewed right now.",
        ) from None

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Pending request not found; it may already have been reviewed.",
        )

    # The review decision is saved. Logging or email failures must not undo it.
    notification_status = "FAILED"
    failure_reason = "Email provider did not confirm success."
    delivery_log_id = None

    company_name = str(record.get("company_name") or "your organization")
    representative_name = str(
        record.get("representative_name") or "Employer"
    )
    recipient = record.get("email")

    if recipient:
        try:
            log = _delivery_log_repository.create_delivery_log(
                recipient=str(recipient),
                channel="EMAIL",
                status="PENDING",
                notification_id=None,
            )
            delivery_log_id = log.get("id") if log else None
        except Exception:
            delivery_log_id = None

        try:
            if payload.status == "Approved":
                subject = (
                    "Your Talent Bridge BD Employer Access Request - Approved"
                )
                plain_text = (
                    f"Dear {representative_name},\n\n"
                    "Thank you for submitting an employer access request "
                    "to Talent Bridge BD. Your request for "
                    f"{company_name} has been reviewed and approved.\n\n"
                    "Our team will complete the necessary organization "
                    "verification and employer account-access setup. "
                    "Approval does not create an account or grant portal "
                    "access. You will receive further instructions once "
                    "your access setup is complete.\n\n"
                    "Kind regards,\nTalent Bridge BD\n"
                    "A Loyal Trade Management Ltd. initiative"
                )
            else:
                subject = (
                    "Update on Your Talent Bridge BD Employer Access Request"
                )
                plain_text = (
                    f"Dear {representative_name},\n\n"
                    "Thank you for your interest in Talent Bridge BD. "
                    "After review, your employer access request for "
                    f"{company_name} has not been approved at this time.\n\n"
                    "If you have questions or believe further information "
                    "may help, please contact the Talent Bridge BD team "
                    "through our official contact channel.\n\n"
                    "Kind regards,\nTalent Bridge BD\n"
                    "A Loyal Trade Management Ltd. initiative"
                )

            safe_plain_text = html.escape(plain_text).replace("\n", "<br>")
            html_content = (
                '<div style="font-family:Arial,sans-serif;line-height:1.6">'
                f"<p>{safe_plain_text}</p>"
                "</div>"
            )

            delivery_result = EmailService().send_email(
                recipient=str(recipient),
                subject=subject,
                html_content=html_content,
                plain_text=plain_text,
            )
            delivery_status = (
                delivery_result.get("status")
                if isinstance(delivery_result, dict)
                else getattr(delivery_result, "status", None)
            )

            if delivery_status == "Succeeded":
                notification_status = "SENT"
                failure_reason = None
            else:
                failure_reason = "Email provider did not confirm success."
        except Exception as exc:
            notification_status = "FAILED"
            failure_reason = f"Email send failed ({type(exc).__name__})."

        if delivery_log_id is not None:
            try:
                _delivery_log_repository.update_delivery_status(
                    delivery_log_id,
                    notification_status,
                    failure_reason,
                )
            except Exception:
                pass

    if notification_status == "SENT":
        message = (
            f"Employer access request {payload.status.lower()}; "
            "notification email sent."
        )
    else:
        message = (
            f"Employer access request {payload.status.lower()}, but the "
            "notification email could not be confirmed as sent. "
            "Please contact the employer separately."
        )

    # This decision does not create a user, role assignment, login,
    # or organization membership.
    return {
        "message": message,
        "notification_status": notification_status,
        "request": record,
    }
