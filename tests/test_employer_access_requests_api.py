from fastapi.testclient import TestClient
from fastapi import HTTPException

from main import app


BASE = "/api/employer-access-requests"

VALID_REQUEST = {
    "company_name": "Example Trading Ltd",
    "representative_name": "Test Representative",
    "email": "Employer@Example.com",
    "phone": "+8801700000000",
    "country": "Bangladesh",
    "industry": "Recruitment",
    "requested_roles": "Steel Fixer",
    "requirements": "Five workers required",
}


def test_public_submission_saves_request_without_granting_access(monkeypatch):
    import api.employer_access_requests as api

    captured = {}

    def fake_create_request(**kwargs):
        captured.update(kwargs)
        return {
            "id": "request-001",
            "status": "Pending",
            "created_at": "2026-10-12T00:00:00",
        }

    monkeypatch.setattr(
        api._repository, "create_request", fake_create_request
    )

    response = TestClient(app).post("/api/public/employer-access-requests", json=VALID_REQUEST)

    assert response.status_code == 201
    assert response.json()["request"]["status"] == "Pending"
    assert captured["email"] == "employer@example.com"
    assert "user_id" not in captured
    assert "role" not in captured
    assert "organization_id" not in captured


def test_public_submission_rejects_invalid_email():
    payload = {**VALID_REQUEST, "email": "not-an-email"}

    response = TestClient(app).post("/api/public/employer-access-requests", json=payload)

    assert response.status_code == 422


def test_request_list_requires_administrator(monkeypatch):
    import api.employer_access_requests as api

    def deny_access(request):
        raise HTTPException(status_code=403, detail="Forbidden")

    monkeypatch.setattr(api, "require_admin", deny_access)

    response = TestClient(app).get(BASE)

    assert response.status_code == 403


def test_administrator_can_list_pending_requests(monkeypatch):
    import api.employer_access_requests as api

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        api._repository,
        "list_requests",
        lambda **kwargs: [
            {"id": "request-001", "status": "Pending"}
        ],
    )

    response = TestClient(app).get(BASE, params={"status": "Pending"})

    assert response.status_code == 200
    assert response.json()["requests"][0]["status"] == "Pending"


def test_review_records_decision_without_creating_membership(monkeypatch):
    import api.employer_access_requests as api
    import services.local_auth as local_auth

    captured = {}

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        local_auth,
        "get_request_principal",
        lambda request: {
            "id": "admin-001",
            "email": "admin@example.com",
        },
    )

    def fake_review_request(request_id, **kwargs):
        captured["request_id"] = request_id
        captured.update(kwargs)
        return {
            "id": request_id,
            "status": kwargs["status"],
            "reviewed_by": kwargs["reviewed_by"],
            "review_notes": kwargs["review_notes"],
        }

    monkeypatch.setattr(
        api._repository, "review_request", fake_review_request
    )

    response = TestClient(app).patch(
        f"{BASE}/request-001/review",
        json={
            "status": "Approved",
            "review_notes": "Company details reviewed",
        },
    )

    assert response.status_code == 200
    assert response.json()["request"]["status"] == "Approved"
    assert captured["reviewed_by"] == "admin@example.com"
    assert captured["review_notes"] == "Company details reviewed"
    assert "organization_id" not in captured
    assert "role" not in captured


def test_review_requires_administrator_identity(monkeypatch):
    import api.employer_access_requests as api
    import services.local_auth as local_auth

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        local_auth, "get_request_principal", lambda request: None
    )

    response = TestClient(app).patch(
        f"{BASE}/request-001/review",
        json={"status": "Rejected"},
    )

    assert response.status_code == 401
