import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from api import administrator_candidate_roles as api
from repositories.application_roles import InMemoryApplicationRoleRepository


client = TestClient(app)


@pytest.fixture
def setup_api(monkeypatch):
    roles = InMemoryApplicationRoleRepository()
    audit = __import__("unittest.mock", fromlist=["Mock"]).Mock()
    principal = {
        "id": "test-admin-001",
        "email": "admin@example.test",
        "name": "Test Admin",
    }
    admin_calls = []

    monkeypatch.setattr(api, "_repository", roles)
    monkeypatch.setattr(api, "_audit_log_repository", audit)
    monkeypatch.setattr(api, "get_request_principal", lambda request: principal)
    monkeypatch.setattr(
        api, "require_admin", lambda request: admin_calls.append(request) or {}
    )

    return roles, audit, principal, admin_calls


def test_grant_candidate_role_is_explicit_and_audited(setup_api):
    roles, audit, principal, admin_calls = setup_api

    response = client.post(
        "/api/administrator/candidate-roles/candidate-123/grant"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "updated"
    assert response.json()["assignment_status"] == "active"
    assert roles.has_role("candidate-123", "Candidate")
    assert len(admin_calls) == 1

    event = audit.create_log.call_args.kwargs
    assert event["user_id"] == principal["id"]
    assert event["entity_id"] == "candidate-123"
    assert event["action"] == "grant"
    assert event["status"] == "success"
    assert event["details"]["role"] == "Candidate"
    assert event["details"]["outcome"] == "changed"


def test_grant_active_candidate_role_is_idempotent(setup_api):
    roles, audit, _, _ = setup_api
    roles.grant_role("candidate-123", "Candidate", assigned_by="earlier-admin")

    response = client.post(
        "/api/administrator/candidate-roles/candidate-123/grant"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "unchanged"
    assert audit.create_log.call_args.kwargs["details"]["outcome"] == "unchanged"


def test_revoke_candidate_role_does_not_change_approval(setup_api):
    roles, audit, _, _ = setup_api
    roles.grant_role("candidate-123", "Candidate", assigned_by="earlier-admin")

    response = client.post(
        "/api/administrator/candidate-roles/candidate-123/revoke"
    )

    assert response.status_code == 200
    assert response.json()["assignment_status"] == "revoked"
    assert not roles.has_role("candidate-123", "Candidate")
    assert audit.create_log.call_args.kwargs["action"] == "revoke"


def test_revoke_missing_role_is_idempotent(setup_api):
    roles, audit, _, _ = setup_api

    response = client.post(
        "/api/administrator/candidate-roles/unknown-user/revoke"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "unchanged"
    assert roles.assignment_status("unknown-user", "Candidate") is None
    assert audit.create_log.call_args.kwargs["details"]["outcome"] == "unchanged"


def test_admin_guard_denial_prevents_role_mutation(monkeypatch):
    roles = InMemoryApplicationRoleRepository()
    monkeypatch.setattr(api, "_repository", roles)

    def deny(request):
        raise HTTPException(status_code=403, detail="Administrator access required")

    monkeypatch.setattr(api, "require_admin", deny)

    response = client.post(
        "/api/administrator/candidate-roles/candidate-123/grant"
    )

    assert response.status_code == 403
    assert roles.assignment_status("candidate-123", "Candidate") is None


def test_audit_failure_after_grant_is_reported_transparently(setup_api):
    roles, audit, _, _ = setup_api
    audit.create_log.side_effect = RuntimeError("audit storage unavailable")

    response = client.post(
        "/api/administrator/candidate-roles/candidate-123/grant"
    )

    assert response.status_code == 500
    assert "role change was applied" in response.json()["detail"]
    assert roles.has_role("candidate-123", "Candidate")
