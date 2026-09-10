from repositories.organization import OrganizationRepository
from services.authorization import AuthorizationContext, build_authorization_context


class AuthorizationService:
    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    def build_context(
        self,
        user_id: str,
        roles: set[str] | list[str] | tuple[str, ...],
    ) -> AuthorizationContext:
        memberships = self.organization_repository.get_active_memberships(
            user_id
        )

        return build_authorization_context(
            user_id=user_id,
            roles=roles,
            memberships=memberships,
        )
