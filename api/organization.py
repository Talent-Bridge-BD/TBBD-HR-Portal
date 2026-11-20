from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    AUTHORIZATION_GROUPS,
    build_authorization_context_from_principal,
    is_global_administrator,
)
from services.local_auth import get_request_principal


router = APIRouter(prefix="/api/organizations", tags=["organizations"])

_organization_repository = SqlOrganizationRepository()


class CreateMembershipRequest(BaseModel):
    user_id: str
    role: str


class UpdateMembershipRequest(BaseModel):
    status: str


def _get_administrator(request: Request) -> dict:
    principal = get_request_principal(request)

    if not principal:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    principal_id = principal.get("id") or ""

    memberships = _organization_repository.get_active_memberships(
        principal_id
    )

    context = build_authorization_context_from_principal(
        principal,
        memberships,
    )

    if not is_global_administrator(context):
        raise HTTPException(
            status_code=403,
            detail="Administrator access is required",
        )

    return principal


@router.get("/{organization_id}/members")
async def list_organization_members(
    organization_id: str,
    request: Request,
):
    _get_administrator(request)

    organizations = _organization_repository.list_active_organizations()

    organization = next(
        (
            organization
            for organization in organizations
            if organization.id == organization_id
        ),
        None,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Active organization not found",
        )

    members = _organization_repository.list_members(organization_id)

    return {
        "organization": {
            "id": organization.id,
            "name": organization.name,
            "status": organization.status,
        },
        "members": [
            {
                "id": member.id,
                "organization_id": member.organization_id,
                "user_id": member.user_id,
                "role": member.role,
                "status": member.status,
            }
            for member in members
        ],
    }


@router.post("/{organization_id}/members", status_code=201)
async def add_organization_member(
    organization_id: str,
    payload: CreateMembershipRequest,
    request: Request,
):
    _get_administrator(request)

    organizations = _organization_repository.list_active_organizations()

    organization = next(
        (
            organization
            for organization in organizations
            if organization.id == organization_id
        ),
        None,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Active organization not found",
        )

    user_id = payload.user_id.strip()
    role = payload.role.strip()

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID is required",
        )

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Membership role is required",
        )

    allowed_roles = {
        "Administrator",
        "HR Manager",
        "Employer Manager",
        "Candidate",
    }

    if role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Unsupported membership role",
        )

    existing_members = _organization_repository.list_members(
        organization_id
    )

    existing = next(
        (
            member
            for member in existing_members
            if member.user_id == user_id
        ),
        None,
    )

    if existing is not None:
        if existing.status != "active":
            member = _organization_repository.update_membership_status(
                organization_id=organization_id,
                user_id=user_id,
                status="active",
                role=role,
            )
            return {
                "membership": {
                    "id": member.id,
                    "organization_id": member.organization_id,
                    "user_id": member.user_id,
                    "role": member.role,
                    "status": member.status,
                },
                "reactivated": True,
            }

        raise HTTPException(
            status_code=409,
            detail="Organization membership already exists",
        )

    member = _organization_repository.add_membership(
        organization_id=organization_id,
        user_id=user_id,
        role=role,
    )

    return {
        "membership": {
            "id": member.id,
            "organization_id": member.organization_id,
            "user_id": member.user_id,
            "role": member.role,
            "status": member.status,
        },
        "reactivated": False,
    }


@router.patch("/{organization_id}/members/{user_id}")
async def update_organization_member(
    organization_id: str,
    user_id: str,
    payload: UpdateMembershipRequest,
    request: Request,
):
    _get_administrator(request)

    status = payload.status.strip().lower()

    if status not in {"active", "inactive", "revoked"}:
        raise HTTPException(
            status_code=400,
            detail="Membership status must be active, inactive, or revoked",
        )

    organizations = _organization_repository.list_active_organizations()

    organization = next(
        (
            organization
            for organization in organizations
            if organization.id == organization_id
        ),
        None,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Active organization not found",
        )

    try:
        member = _organization_repository.update_membership_status(
            organization_id=organization_id,
            user_id=user_id,
            status=status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "membership": {
            "id": member.id,
            "organization_id": member.organization_id,
            "user_id": member.user_id,
            "role": member.role,
            "status": member.status,
        }
    }
