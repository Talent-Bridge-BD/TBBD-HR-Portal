import base64
import json

from fastapi.testclient import TestClient

import api.screening as screening_api
from main import app


ORGANIZATION_ID = "005F50D3-26AB-F111-9B32-000D3AC9134A"
OTHER_ORGANIZATION_ID = "105F50D3-26AB-F111-9B32-000D3AC9134A"
APPLICATION_ID = "6528C71E-FEAD-F111-9B33-000D3AC8B575"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


def make_principal(principal_id, name, groups=None, roles=None):
    principal = {
        "claims": [
            {"typ": "name", "val": name},
            *[
                {"typ": "groups", "val": group}
                for group in (groups or [])
            ],
            *[
                {"typ": "roles", "val": role}
                for role in (roles or [])
            ],
        ]
    }

    return base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")


def auth_headers(groups=None, roles=None):
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": "user-001",
        "X-MS-CLIENT-PRINCIPAL-NAME": "test-user@example.test",
        "X-MS-CLIENT-PRINCIPAL": make_principal(
            "user-001",
            "Test User",
            groups=groups,
            roles=roles,
        ),
    }


def test_screening_get_requires_authentication():
    client = TestClient(app)

    response = client.get(
        f"/api/screening/application/{APPLICATION_ID}"
        f"?organization_id={ORGANIZATION_ID}",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authenticated user identity is required"
    )


def test_screening_rejects_user_without_management_role_before_membership_lookup(
    monkeypatch,
):
    def unexpected_membership_lookup(user_id):
        raise AssertionError(
            "Membership lookup must not run before role authorization"
        )

    monkeypatch.setattr(
        screening_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: unexpected_membership_lookup(user_id)
                )
            },
        )(),
    )

    client = TestClient(app)

    response = client.get(
        f"/api/screening/application/{APPLICATION_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Recruitment management role is required"
    )


def test_screening_administrator_bypasses_organization_membership(
    monkeypatch,
):
    monkeypatch.setattr(
        screening_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": lambda self, user_id: [],
            },
        )(),
    )

    monkeypatch.setattr(
        screening_api,
        "_application_repository",
        type(
            "FakeApplicationRepository",
            (),
            {
                "get_application": (
                    lambda self, organization_id, application_id: None
                ),
            },
        )(),
    )

    client = TestClient(app)

    response = client.get(
        f"/api/screening/application/{APPLICATION_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(groups=[ADMINISTRATOR_GROUP_ID]),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Application not found for this organization"
    )


def test_screening_employer_manager_requires_matching_organization_membership(
    monkeypatch,
):
    monkeypatch.setattr(
        screening_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": lambda self, user_id: [
                    type(
                        "Membership",
                        (),
                        {
                            "user_id": user_id,
                            "organization_id": OTHER_ORGANIZATION_ID,
                            "status": "active",
                            "role": "Employer Manager",
                        },
                    )()
                ],
            },
        )(),
    )

    client = TestClient(app)

    response = client.get(
        f"/api/screening/application/{APPLICATION_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(roles=["Employer Manager"]),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "User is not authorized for this organization"
    )