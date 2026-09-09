from dataclasses import dataclass


@dataclass(frozen=True)
class Organization:
    id: str
    name: str
    status: str = "active"


@dataclass(frozen=True)
class OrganizationMembership:
    user_id: str
    organization_id: str
    role: str
    status: str = "active"
