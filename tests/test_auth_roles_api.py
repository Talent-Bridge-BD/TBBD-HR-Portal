import main
from fastapi.testclient import TestClient
from api import candidate as candidate_api
from repositories.application_roles import InMemoryApplicationRoleRepository
from repositories.candidate_approvals import InMemoryCandidateApprovalRepository
from models.user_profile import UserProfile

client = TestClient(main.app)

CANDIDATE_TENANT_ID = "c8573333-aad0-4a28-8e40-c20e17989f61"
ADMIN_GROUP_ID = "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"


def get_me_with_principal(monkeypatch, principal, approved_candidate=False):
    roles = InMemoryApplicationRoleRepository()
    approvals = InMemoryCandidateApprovalRepository()
    monkeypatch.setattr(candidate_api, "_application_role_repository", roles)
    monkeypatch.setattr(candidate_api, "_approval_repository", approvals)

    user_id = principal.get("application_user_id", principal["id"])
    email = principal.get("email", "")

    monkeypatch.setattr(
        main._user_profile_repository,
        "get_by_email",
        lambda requested_email: (
            UserProfile(user_id=user_id, primary_email=requested_email)
            if requested_email
            and requested_email.casefold() == email.casefold()
            else None
        ),
    )

    if approved_candidate:
        approvals.ensure_candidate(user_id)
        approvals.review_candidate(
            user_id,
            status="approved",
            reviewed_by="test-admin",
            approval_notes=None,
        )
        roles.grant_role(user_id, "Candidate", assigned_by="test-admin")
    elif principal.get("assign_candidate_role"):
        roles.grant_role(user_id, "Candidate", assigned_by="test-admin")

    monkeypatch.setattr(
        main,
        "get_request_principal",
        lambda request: principal,
    )
    monkeypatch.setattr(
        main._organization_repository,
        "get_active_memberships",
        lambda user_id: [],
    )
    return client.get("/api/me")


def test_external_id_candidate_receives_role_only_when_approved(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-candidate",
            "email": "candidate@example.test",
            "name": "Test Candidate",
            "tenant_id": CANDIDATE_TENANT_ID,
            "claims": [
                {"typ": "tid", "val": CANDIDATE_TENANT_ID},
            ],
        },
        approved_candidate=True,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "Candidate" in data["roles"]
    assert "Employee" not in data["roles"]


def test_external_id_candidate_with_role_receives_role_while_pending(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-pending-assigned-candidate",
            "email": "pending@example.test",
            "tenant_id": CANDIDATE_TENANT_ID,
            "claims": [{"typ": "tid", "val": CANDIDATE_TENANT_ID}],
            "assign_candidate_role": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "Candidate" in data["roles"]
    assert "Employee" not in data["roles"]


def test_external_id_candidate_without_role_is_not_candidate(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-pending-candidate",
            "email": "pending@example.test",
            "tenant_id": CANDIDATE_TENANT_ID,
            "claims": [{"typ": "tid", "val": CANDIDATE_TENANT_ID}],
        },
    )

    assert response.status_code == 200
    assert "Candidate" not in response.json()["roles"]
    assert "Employee" not in response.json()["roles"]


def test_workforce_administrator_role_is_preserved(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-admin",
            "email": "admin@example.test",
            "name": "Test Administrator",
            "claims": [
                {"typ": "groups", "val": ADMIN_GROUP_ID},
            ],
        },
    )

    assert response.status_code == 200
    assert "Administrator" in response.json()["roles"]


def test_workforce_user_keeps_employee_default(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-employee",
            "email": "employee@example.test",
            "name": "Test Employee",
            "claims": [],
        },
    )

    assert response.status_code == 200
    assert "Employee" in response.json()["roles"]
    assert "Candidate" not in response.json()["roles"]
