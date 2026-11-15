from __future__ import annotations

import html
import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.administrator_organizations import require_admin
from api import organization as organization_api
from repositories.employer_access_requests import (
    EmployerAccessRequestRepository,
)

from services.email_service import EmailService
from repositories.administrator_notifications import AdministratorNotificationRepository
from repositories.external_identity import SqlExternalIdentityMappingRepository
from services.local_auth import (
    TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER,
    TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
)

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
_identity_mapping_repository = SqlExternalIdentityMappingRepository(
    organization_api._organization_repository._connection
)


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


class EmployerAccessRequestActivation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    organization_id: str = Field(min_length=1, max_length=100)
    entra_object_id: str = Field(min_length=1, max_length=200)
    identity_verified: bool
    # Supply only when linking an already-existing application account.
    # Omit for the existing new-employer activation workflow.
    application_user_id: str | None = Field(default=None, min_length=1, max_length=100)




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


@router.post("/{request_id}/activate")
def activate_approved_employer_request(
    request: Request,
    request_id: str,
    payload: EmployerAccessRequestActivation,
):
    """Activate an approved request for an administrator-verified Entra identity."""
    principal = require_admin(request)

    if payload.identity_verified is not True:
        raise HTTPException(
            status_code=400,
            detail="Confirm that the Microsoft Entra identity was independently verified.",
        )

    try:
        from services.local_auth import get_request_principal
        authenticated_principal = get_request_principal(request)
    except Exception:
        authenticated_principal = None

    administrator_id = (
        str(authenticated_principal.get("id"))
        if authenticated_principal and authenticated_principal.get("id")
        else None
    )
    if not administrator_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated Administrator identity required",
        )

    try:
        record = _repository.get_request(request_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from None
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The employer access request could not be retrieved.",
        ) from None

    if record is None:
        raise HTTPException(status_code=404, detail="Employer access request not found.")
    if record.get("status") != "Approved":
        raise HTTPException(
            status_code=409,
            detail="Only an Approved employer access request can be activated.",
        )

    organization_id = payload.organization_id.strip()
    entra_object_id = payload.entra_object_id.strip()

    try:
        organizations = organization_api._organization_repository.list_active_organizations()
        organization = next(
            (item for item in organizations if str(item.id) == organization_id),
            None,
        )
        if organization is None:
            raise HTTPException(status_code=404, detail="Active organization not found.")

        members = organization_api._organization_repository.list_members(organization_id)

        if payload.application_user_id:
            # Existing-account linking is deliberately separate from creating
            # or changing organization memberships. The target must already
            # have an active Employer Manager membership in this organization.
            application_user_id = payload.application_user_id.strip()
            member = next(
                (
                    item for item in members
                    if str(item.user_id) == application_user_id
                    and str(item.status).lower() == "active"
                    and str(item.role).strip().lower() == "employer manager"
                ),
                None,
            )
            if member is None:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "The selected application account does not have an active "
                        "Employer Manager membership in this organization."
                    ),
                )

            existing_mapping = _identity_mapping_repository.get_mapping(
                provider=TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER,
                tenant_id=TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
                external_object_id=entra_object_id,
            )
            if existing_mapping is not None:
                raise HTTPException(
                    status_code=409,
                    detail="This external identity already has a mapping. Review it before making changes.",
                )

            try:
                mapping = _identity_mapping_repository.create_active_mapping(
                    provider=TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER,
                    tenant_id=TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
                    external_object_id=entra_object_id,
                    application_user_id=application_user_id,
                    verified_by=administrator_id,
                    verification_method="administrator_attestation",
                )
            except Exception:
                # A concurrent request may have claimed the unique external
                # identity. Report a conflict if the mapping now exists; let
                # genuine database failures reach the service-unavailable path.
                if _identity_mapping_repository.get_mapping(
                    provider=TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER,
                    tenant_id=TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
                    external_object_id=entra_object_id,
                ) is not None:
                    raise HTTPException(
                        status_code=409,
                        detail="This external identity already has a mapping. Review it before making changes.",
                    ) from None
                raise
            membership_action = "link"
            audit_entity_type = "external_identity_mapping"
            audit_entity_id = str(mapping["id"])
            audit_target_user_id = application_user_id
        else:
            # Preserve the existing new-employer activation behaviour.
            existing = next(
                (member for member in members if str(member.user_id) == entra_object_id),
                None,
            )

            if existing is not None:
                if str(existing.status).lower() == "active":
                    raise HTTPException(
                        status_code=409,
                        detail="This Entra identity already has an active membership in the selected organization.",
                    )
                if existing.role != "Employer Manager":
                    raise HTTPException(
                        status_code=409,
                        detail="An inactive membership exists with a different role. Review it separately before activation.",
                    )
                member = organization_api._organization_repository.update_membership_status(
                    organization_id=organization_id,
                    user_id=entra_object_id,
                    status="active",
                    role="Employer Manager",
                )
                membership_action = "reactivate"
            else:
                member = organization_api._organization_repository.add_membership(
                    organization_id=organization_id,
                    user_id=entra_object_id,
                    role="Employer Manager",
                )
                membership_action = "create"
            audit_entity_type = "organization_membership"
            audit_entity_id = str(member.id)
            audit_target_user_id = entra_object_id
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Organization membership could not be activated.",
        ) from None

    # Record the membership action. The mapping or membership has already
    # committed independently, so an audit failure must be reported honestly.
    audit_status = "SUCCESS"
    try:
        organization_api._audit_log_repository.create_log(
            user_id=administrator_id,
            user_email=authenticated_principal.get("email"),
            user_name=authenticated_principal.get("name"),
            organization_id=organization_id,
            event_type=(
                "external_identity_mapping"
                if membership_action == "link"
                else "organization_membership"
            ),
            action=membership_action,
            entity_type=audit_entity_type,
            entity_id=audit_entity_id,
            status="success",
            details={
                "organization_name": organization.name,
                "target_user_id": audit_target_user_id,
                "external_object_id": entra_object_id,
                "identity_provider": TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER,
                "identity_tenant_id": TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
                "role": "Employer Manager",
                "access_request_id": str(record.get("id")),
                "identity_verification_confirmed_by_admin": True,
                "verification_method": (
                    "administrator_attestation"
                    if membership_action == "link"
                    else "administrator_verified_activation"
                ),
            },
        )
    except Exception:
        audit_status = "FAILED"

    notification_status = "FAILED"
    failure_reason = "Email provider did not confirm success."
    delivery_log_id = None
    recipient = str(record.get("email") or "").strip()

    if recipient:
        try:
            log = _delivery_log_repository.create_delivery_log(
                recipient=recipient,
                channel="EMAIL",
                status="PENDING",
                notification_id=None,
            )
            delivery_log_id = log.get("id") if log else None
        except Exception:
            delivery_log_id = None

        company_name = str(record.get("company_name") or "your organization")
        representative_name = str(record.get("representative_name") or "Employer")
        portal_url = "https://employer.talentbridgebd.com"
        plain_text = (
            f"Dear {representative_name},\n\n"
            f"Your employer access request for {company_name} has been activated "
            f"for the selected organization, {organization.name}.\n\n"
            "Sign in to the Talent Bridge BD portal using Microsoft Entra ID "
            "with the identity verified by our administrator. This email does "
            "not create a password or replace your organization's sign-in policy.\n\n"
            f"Portal: {portal_url}\n\n"
            "If you cannot sign in, contact the Talent Bridge BD administrator.\n\n"
            "Kind regards,\nTalent Bridge BD"
        )
        html_content = (
            '<div style="font-family:Arial,sans-serif;line-height:1.6">'
            f"<p>{html.escape(plain_text).replace(chr(10), '<br>')}</p>"
            "</div>"
        )

        try:
            result = EmailService().send_email(
                recipient=recipient,
                subject="Your Talent Bridge BD Employer Access Is Active",
                html_content=html_content,
                plain_text=plain_text,
            )
            result_status = (
                result.get("status")
                if isinstance(result, dict)
                else getattr(result, "status", None)
            )
            if result_status == "Succeeded":
                notification_status = "SENT"
                failure_reason = None
        except Exception as exc:
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

    return {
        "message": (
            "Employer access is active, but audit logging failed. Administrator follow-up is required."
            if audit_status == "FAILED"
            else (
                "Employer membership is active. Activation email sent."
                if notification_status == "SENT"
                else "Employer membership is active, but the activation email could not be confirmed as sent."
            )
        ),
        "membership_status": "ACTIVE",
        "audit_status": audit_status,
        "requires_admin_follow_up": audit_status == "FAILED",
        "audit_warning": (
            "The membership or identity mapping is active, but its audit record could not be saved."
            if audit_status == "FAILED"
            else None
        ),
        "role": "Employer Manager",
        "organization": {
            "id": organization.id,
            "name": organization.name,
        },
        "notification_status": notification_status,
        "request": record,
    }
