from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationMembership:
    id: str
    organization_id: str
    user_id: str
    role: str
    status: str
