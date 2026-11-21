import base64
import json

from fastapi import APIRouter, HTTPException, Request

from repositories.application import SqlApplicationRepository
from repositories.candidate_document import SqlCandidateDocumentRepository
from repositories.blob_storage import BlobStorageRepository
from repositories.organization import SqlOrganizationRepository
from services.application import ApplicationService
from services.authorization import (
    build_authorization_context_from_principal,
    is_global_administrator,
)
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/applications",
    tags=["applications"],
)

_application_repository = SqlApplicationRepository()
_application_service = ApplicationService(
    _application_repository,
)
_organization_repository = SqlOrganizationRepository()
_candidate_document_repository = SqlCandidateDocumentRepository()
_blob_repository = BlobStorageRepository()


def get_application_authorization_context(
    request: Request,
):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    principal_id = principal["id"]
    memberships = _organization_repository.get_active_memberships(
        principal_id,
    )

    context = build_authorization_context_from_principal(
        principal=principal,
        memberships=memberships,
    )

    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not context.roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Employer management role is required",
        )

    return context

def _require_organization_access(
    request: Request,
    organization_id: str,
):
    context = get_application_authorization_context(request)

    if is_global_administrator(context):
        return context

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.get("")
async def list_applications(
    request: Request,
    organization_id: str | None = None,
):
    context = get_application_authorization_context(request)

    if is_global_administrator(context) and not organization_id:
        applications = _application_service.list_all_active_organization_applications()
    else:
        if not organization_id:
            raise HTTPException(
                status_code=400,
                detail="organization_id is required",
            )

        _require_organization_access(
            request,
            organization_id,
        )

        applications = _application_service.list_applications(
            organization_id,
        )

    return {
        "applications": [
            item.__dict__
            for item in applications
        ]
    }


@router.put("/{application_id}/status")
async def update_application_status(
    application_id: str,
    organization_id: str,
    status: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )
    allowed_statuses = {
        "submitted",
        "under_review",
        "shortlisted",
        "interview",
        "offered",
        "hired",
        "rejected",
    }

    normalized_status = status.strip().lower()

    if normalized_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid application status: {status}",
        )

    application = _application_service.update_status(
        organization_id,
        application_id,
        normalized_status,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return {
        "application": application.__dict__,
        "message": "Application status updated successfully",
    }



@router.get("/{application_id}/documents")
async def list_application_documents(
    application_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    application = _application_service.get_application(
        organization_id,
        application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    documents = _candidate_document_repository.list_documents_for_application(
        organization_id,
        application_id,
    )

    return {
        "documents": [document.__dict__ for document in documents],
    }

@router.get("/{application_id}/documents/{document_id}")
async def view_application_document(
    application_id: str,
    document_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    application = _application_service.get_application(
        organization_id,
        application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    document = _candidate_document_repository.get_document(
        application.candidate_id,
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
                f'inline; filename="{document.file_name}"'
            )
        },
    )


@router.get("/{application_id}")
async def get_application(
    application_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    application = _application_service.get_application(
        organization_id,
        application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return {
        "application": application.__dict__
    }
