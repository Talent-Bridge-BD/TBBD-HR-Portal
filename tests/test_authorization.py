from repositories.organization import InMemoryOrganizationRepository
from models.organization import OrganizationMembership
from services.authorization_service import AuthorizationService


def test_authorization_context_contains_only_active_user_memberships():
    repository = InMemoryOrganizationRepository()

    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id="org-001",
            user_id="user-001",
            role="Employer Manager",
            status="active",
        ),
        OrganizationMembership(
            id="membership-002",
            organization_id="org-002",
            user_id="user-001",
            role="Employer Manager",
            status="revoked",
        ),
        OrganizationMembership(
            id="membership-003",
            organization_id="org-003",
            user_id="user-002",
            role="Employer Manager",
            status="active",
        ),
    ]

    service = AuthorizationService(repository)

    context = service.build_context(
        user_id="user-001",
        roles={"Employer Manager"},
    )

    assert context.user_id == "user-001"
    assert context.roles == frozenset({"Employer Manager"})
    assert context.organization_ids == frozenset({"org-001"})
