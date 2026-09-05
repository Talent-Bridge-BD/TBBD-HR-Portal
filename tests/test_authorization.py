import unittest

from models.organization import OrganizationMembership
from services.authorization import (
    build_authorization_context,
    has_organization_access,
    has_role,
)


class AuthorizationTests(unittest.TestCase):

    def test_employer_manager_can_access_authorized_organization(self):
        context = build_authorization_context(
            user_id="user-1",
            roles={"Employer Manager"},
            memberships=[
                OrganizationMembership(
                    user_id="user-1",
                    organization_id="org-a",
                    role="Employer Manager",
                )
            ],
        )

        self.assertTrue(has_role(context, "Employer Manager"))
        self.assertTrue(has_organization_access(context, "org-a"))
        self.assertFalse(has_organization_access(context, "org-b"))

    def test_inactive_membership_does_not_grant_access(self):
        context = build_authorization_context(
            user_id="user-1",
            roles={"Employer Manager"},
            memberships=[
                OrganizationMembership(
                    user_id="user-1",
                    organization_id="org-a",
                    role="Employer Manager",
                    status="inactive",
                )
            ],
        )

        self.assertFalse(has_organization_access(context, "org-a"))

    def test_membership_for_another_user_does_not_grant_access(self):
        context = build_authorization_context(
            user_id="user-1",
            roles={"Employer Manager"},
            memberships=[
                OrganizationMembership(
                    user_id="user-2",
                    organization_id="org-a",
                    role="Employer Manager",
                )
            ],
        )

        self.assertFalse(has_organization_access(context, "org-a"))


if __name__ == "__main__":
    unittest.main()
