import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

CANDIDATE_TENANT_ID = "c8573333-aad0-4a28-8e40-c20e17989f61"
ADMIN_GROUP_ID = "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"


def get_me_with_principal(monkeypatch, principal):
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


def test_external_id_candidate_receives_candidate_role(monkeypatch):
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
    )

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "Candidate" in data["roles"]
    assert "Employee" not in data["roles"]


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
