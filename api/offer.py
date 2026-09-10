import base64
import json
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.offer import SqlOfferRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context
from services.offer import OfferService


router = APIRouter(prefix="/api/offers", tags=["offers"])

_offer_repository = SqlOfferRepository()
_offer_service = OfferService(_offer_repository)
_organization_repository = SqlOrganizationRepository()


EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


ALLOWED_STATUSES = {
    "draft",
    "sent",
    "accepted",
    "declined",
    "expired",
    "withdrawn",
}


class CreateOfferRequest(BaseModel):
    application_id: str
    offer_date: datetime
    expiry_date: Optional[datetime] = None
    start_date: Optional[date] = None
    employment_type: Optional[str] = None
    salary_compensation: Optional[str] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class UpdateOfferRequest(BaseModel):
    offer_date: datetime
    expiry_date: Optional[datetime] = None
    start_date: Optional[date] = None
    employment_type: Optional[str] = None
    salary_compensation: Optional[str] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    status: str


def _claim_values(principal: dict, claim_type: str) -> list[str]:
    values = []

    for claim in principal.get("claims", []):
        if claim.get("typ") == claim_type:
            value = claim.get("val")
            if value:
                values.append(value)

    return values


def get_offer_authorization_context(request: Request):
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    principal_header = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not principal_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    if not principal_header:
        raise HTTPException(
            status_code=401,
            detail="Authenticated principal is required",
        )

    try:
        principal = json.loads(
            base64.b64decode(principal_header).decode("utf-8")
        )
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated principal",
        ) from exc

    groups = set(_claim_values(principal, "groups"))
    token_roles = set(_claim_values(principal, "roles"))

    roles = set(token_roles)

    if EMPLOYER_MANAGER_GROUP_ID in groups:
        roles.add("Employer Manager")

    if HR_MANAGER_GROUP_ID in groups:
        roles.add("HR Manager")

    if ADMINISTRATOR_GROUP_ID in groups:
        roles.add("Administrator")

    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for recruitment offers",
        )

    memberships = _organization_repository.list_active_memberships(
        principal_id
    )

    return build_authorization_context(
        principal_id=principal_id,
        roles=roles,
        memberships=memberships,
    )


def _require_organization_access(
    request: Request,
    organization_id: str,
):
    auth_context = get_offer_authorization_context(request)

    organization = _organization_repository.get_organization(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    if not any(
        str(membership.organization_id) == str(organization_id)
        for membership in auth_context.organization_memberships
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this organization",
        )

    return auth_context


@router.get("")
def list_offers(
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    return _offer_service.list_offers(
        organization_id,
    )


@router.get("/{offer_id}")
def get_offer(
    offer_id: str,
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    offer = _offer_service.get_offer(
        organization_id,
        offer_id,
    )

    if offer is None:
        raise HTTPException(
            status_code=404,
            detail="Offer not found",
        )

    return offer


@router.post("")
def create_offer(
    payload: CreateOfferRequest,
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    try:
        return _offer_service.create_offer(
            organization_id=organization_id,
            application_id=payload.application_id,
            offer_date=payload.offer_date,
            expiry_date=payload.expiry_date,
            start_date=payload.start_date,
            employment_type=payload.employment_type,
            salary_compensation=payload.salary_compensation,
            currency=payload.currency,
            location=payload.location,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.put("/{offer_id}")
def update_offer(
    offer_id: str,
    payload: UpdateOfferRequest,
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    if payload.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid offer status",
        )

    try:
        offer = _offer_service.update_offer(
            organization_id=organization_id,
            offer_id=offer_id,
            offer_date=payload.offer_date,
            expiry_date=payload.expiry_date,
            start_date=payload.start_date,
            employment_type=payload.employment_type,
            salary_compensation=payload.salary_compensation,
            currency=payload.currency,
            location=payload.location,
            notes=payload.notes,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if offer is None:
        raise HTTPException(
            status_code=404,
            detail="Offer not found",
        )

    return offer
