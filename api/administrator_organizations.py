from fastapi import APIRouter, Request

from api.administrator import _get_administrator_context
from repositories.organization import SqlOrganizationRepository


router = APIRouter(
    prefix="/api/administrator/organizations",
    tags=["administrator-organizations"],
)

_repository = SqlOrganizationRepository()


def require_admin(request: Request):
    """Use the shared Administrator authorization implementation."""
    return _get_administrator_context(request)


@router.get("")
def list_organizations(request: Request):
    require_admin(request)

    organizations = _repository.list_active_organizations()

    return {
        "organizations": [
            {
                "id": organization.id,
                "name": organization.name,
                "status": organization.status,
            }
            for organization in organizations
        ]
    }
