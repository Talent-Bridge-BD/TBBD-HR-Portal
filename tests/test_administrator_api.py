from fastapi.testclient import TestClient

from main import app
from api import administrator as api


client = TestClient(app)


class FakeOrganizationRepository:
    def get_active_memberships(self, user_id):
        return []

    def list_active_organizations(self):
        return []

    def list_all_members(self):
        return []


def setup_admin_api(monkeypatch, principal):
    monkeypatch.setattr(
        api,
        "get_request_principal",
        lambda request: principal,
    )
    monkeypatch.setattr(
        api,
        "_organization_repository",
        FakeOrganizationRepository(),
    )
    monkeypatch.setattr(
        api.application_role_repository,
        "has_role",
        lambda user_id, role: False,
    )


def test_dashboard_accepts_trusted_administrator_role_claim(monkeypatch):
    principal = {
        "id": "test-admin-001",
        "email": "admin@example.test",
        "claims": [
            {"typ": "roles", "val": "Administrator"},
        ],
    }
    setup_admin_api(monkeypatch, principal)

    def profile_lookup_must_not_be_needed(email):
        raise RuntimeError("SQL profile lookup unavailable")

    monkeypatch.setattr(
        api._user_profile_repository,
        "get_by_email",
        profile_lookup_must_not_be_needed,
    )

    response = client.get("/api/administrator/dashboard")

    assert response.status_code == 200
    assert response.json()["organizations"]["total"] == 0


def test_dashboard_rejects_principal_without_administrator_role(monkeypatch):
    principal = {
        "id": "test-user-001",
        "email": "user@example.test",
        "claims": [
            {"typ": "roles", "val": "Employer Manager"},
        ],
    }
    setup_admin_api(monkeypatch, principal)

    monkeypatch.setattr(
        api._user_profile_repository,
        "get_by_email",
        lambda email: None,
    )

    response = client.get("/api/administrator/dashboard")

    assert response.status_code == 403
    assert response.json()["detail"] == "Administrator access required"
