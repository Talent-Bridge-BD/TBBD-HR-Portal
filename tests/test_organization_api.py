import base64
import json

from fastapi.testclient import TestClient

from main import app
from models.organization import Organization, OrganizationMembership
from repositories.organization import InMemoryOrganizationRepository


ADMIN_ID = "admin-001"
EMPLOYER_ID = "employer-001"
ORG_ID = "org-001"


def make_principal(principal_id, name, roles=None):
    principal = {
        "claims": [
            {"typ": "name", "val": name},
            *[
                {"typ": "roles", "val": role}
                for role in (roles or [])
            ],
        ]
    }
    return base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")


def admin_headers():
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": ADMIN_ID,
        "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.com",
        "X-MS-CLIENT-PRINCIPAL": make_principal(
            ADMIN_ID,
            "Test Administrator",
            roles=["Administrator"],
        ),
    }


def employer_headers():
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": EMPLOYER_ID,
        "X-MS-CLIENT-PRINCIPAL-NAME": "employer@example.com",
        "X-MS-CLIENT-PRINCIPAL": make_principal(
            EMPLOYER_ID,
            "Test Employer",
            roles=["Employer Manager"],
        ),
    }


def make_repository():
    repository = InMemoryOrganizationRepository()
    repository._organizations = [
        Organization(
            id=ORG_ID,
            name="Talent Bridge BD",
            status="active",
        ),
        Organization(
            id="org-inactive",
            name="Inactive Organization",
            status="inactive",
        ),
    ]
    return repository


def test_administrator_can_list_organization_members(monkeypatch):
    import api.organization as organization_api

    repository = make_repository()
    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id=ORG_ID,
            user_id=EMPLOYER_ID,
            role="Employer Manager",
            status="active",
        ),
    ]
    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        repository,
    )

    response = TestClient(app).get(
        f"/api/organizations/{ORG_ID}/members",
        headers=admin_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["organization"]["id"] == ORG_ID
    assert data["organization"]["name"] == "Talent Bridge BD"
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == EMPLOYER_ID


def test_non_administrator_cannot_list_organization_members(monkeypatch):
    import api.organization as organization_api

    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        make_repository(),
    )

    response = TestClient(app).get(
        f"/api/organizations/{ORG_ID}/members",
        headers=employer_headers(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Administrator access is required"


def test_non_administrator_cannot_create_membership(monkeypatch):
    import api.organization as organization_api

    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        make_repository(),
    )

    response = TestClient(app).post(
        f"/api/organizations/{ORG_ID}/members",
        headers=employer_headers(),
        json={
            "user_id": "new-user-001",
            "role": "Employer Manager",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Administrator access is required"


def test_non_administrator_cannot_update_membership(monkeypatch):
    import api.organization as organization_api

    repository = make_repository()
    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id=ORG_ID,
            user_id=EMPLOYER_ID,
            role="Employer Manager",
            status="active",
        ),
    ]
    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        repository,
    )

    response = TestClient(app).patch(
        f"/api/organizations/{ORG_ID}/members/{EMPLOYER_ID}",
        headers=employer_headers(),
        json={"status": "revoked"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Administrator access is required"


def test_unknown_or_inactive_organization_returns_404(monkeypatch):
    import api.organization as organization_api

    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        make_repository(),
    )

    response = TestClient(app).get(
        "/api/organizations/org-inactive/members",
        headers=admin_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Active organization not found"


def test_administrator_can_create_membership(monkeypatch):
    import api.organization as organization_api

    repository = make_repository()
    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        repository,
    )

    response = TestClient(app).post(
        f"/api/organizations/{ORG_ID}/members",
        headers=admin_headers(),
        json={
            "user_id": EMPLOYER_ID,
            "role": "Employer Manager",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["reactivated"] is False
    assert data["membership"]["organization_id"] == ORG_ID
    assert data["membership"]["user_id"] == EMPLOYER_ID
    assert data["membership"]["role"] == "Employer Manager"
    assert data["membership"]["status"] == "active"


def test_duplicate_active_membership_returns_409(monkeypatch):
    import api.organization as organization_api

    repository = make_repository()
    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id=ORG_ID,
            user_id=EMPLOYER_ID,
            role="Employer Manager",
            status="active",
        ),
    ]
    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        repository,
    )

    response = TestClient(app).post(
        f"/api/organizations/{ORG_ID}/members",
        headers=admin_headers(),
        json={
            "user_id": EMPLOYER_ID,
            "role": "Employer Manager",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Organization membership already exists"
    )


def test_inactive_membership_can_be_reactivated(monkeypatch):
    import api.organization as organization_api

    repository = make_repository()
    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id=ORG_ID,
            user_id=EMPLOYER_ID,
            role="Employer Manager",
            status="inactive",
        ),
    ]
    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        repository,
    )

    response = TestClient(app).post(
        f"/api/organizations/{ORG_ID}/members",
        headers=admin_headers(),
        json={
            "user_id": EMPLOYER_ID,
            "role": "Employer Manager",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["reactivated"] is True
    assert data["membership"]["status"] == "active"
    assert data["membership"]["role"] == "Employer Manager"


def test_patch_can_revoke_membership(monkeypatch):
    import api.organization as organization_api

    repository = make_repository()
    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id=ORG_ID,
            user_id=EMPLOYER_ID,
            role="Employer Manager",
            status="active",
        ),
    ]
    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        repository,
    )

    response = TestClient(app).patch(
        f"/api/organizations/{ORG_ID}/members/{EMPLOYER_ID}",
        headers=admin_headers(),
        json={"status": "revoked"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["membership"]["status"] == "revoked"


def test_patch_preserves_membership_role(monkeypatch):
    import api.organization as organization_api

    repository = make_repository()
    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id=ORG_ID,
            user_id=EMPLOYER_ID,
            role="Employer Manager",
            status="active",
        ),
    ]
    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        repository,
    )

    response = TestClient(app).patch(
        f"/api/organizations/{ORG_ID}/members/{EMPLOYER_ID}",
        headers=admin_headers(),
        json={"status": "inactive"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["membership"]["status"] == "inactive"
    assert data["membership"]["role"] == "Employer Manager"


def test_invalid_membership_role_is_rejected(monkeypatch):
    import api.organization as organization_api

    monkeypatch.setattr(
        organization_api,
        "_organization_repository",
        make_repository(),
    )

    response = TestClient(app).post(
        f"/api/organizations/{ORG_ID}/members",
        headers=admin_headers(),
        json={
            "user_id": EMPLOYER_ID,
            "role": "Super Administrator",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported membership role"
