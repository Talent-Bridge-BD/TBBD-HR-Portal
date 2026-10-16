from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from api import administrator_candidate_approvals as api
from repositories.candidate_approvals import InMemoryCandidateApprovalRepository


def setup_api(monkeypatch):
    repository = InMemoryCandidateApprovalRepository()
    monkeypatch.setattr(api, "_repository", repository)
    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        api,
        "get_request_principal",
        lambda request: {"id": "test-admin-001"},
    )
    return repository, TestClient(app)


def test_list_approvals_requires_administrator(monkeypatch):
    monkeypatch.setattr(
        api,
        "require_admin",
        lambda request: (_ for _ in ()).throw(
            HTTPException(status_code=403, detail="Administrator access required")
        ),
    )

    response = TestClient(app).get(
        "/api/administrator/candidate-approvals"
    )

    assert response.status_code == 403


def test_list_approvals_returns_items_and_pagination(monkeypatch):
    repository, client = setup_api(monkeypatch)
    repository.ensure_candidate("candidate-001")
    repository.ensure_candidate("candidate-002")

    response = client.get(
        "/api/administrator/candidate-approvals",
        params={"limit": 1, "offset": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["limit"] == 1
    assert body["offset"] == 0
    assert body["has_more"] is True


def test_admin_can_approve_pending_candidate(monkeypatch):
    repository, client = setup_api(monkeypatch)
    repository.ensure_candidate("candidate-001")

    response = client.post(
        "/api/administrator/candidate-approvals/candidate-001/review",
        json={
            "status": "approved",
            "approval_notes": "Profile reviewed",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["item"]["approval_status"] == "approved"
    assert body["item"]["reviewed_by"] == "test-admin-001"
    assert body["item"]["approval_notes"] == "Profile reviewed"


def test_repeat_review_cannot_overwrite_decision(monkeypatch):
    repository, client = setup_api(monkeypatch)
    repository.ensure_candidate("candidate-001")

    first = client.post(
        "/api/administrator/candidate-approvals/candidate-001/review",
        json={"status": "approved"},
    )
    second = client.post(
        "/api/administrator/candidate-approvals/candidate-001/review",
        json={"status": "rejected"},
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert (
        repository.get_approval("candidate-001")["approval_status"]
        == "approved"
    )


def test_bulk_approval_reports_approved_and_skipped(monkeypatch):
    repository, client = setup_api(monkeypatch)
    repository.ensure_candidate("candidate-001")
    repository.ensure_candidate("candidate-002")
    repository.review_candidate(
        "candidate-002",
        status="rejected",
        reviewed_by="another-admin",
    )

    response = client.post(
        "/api/administrator/candidate-approvals/bulk-approve",
        json={
            "entra_object_ids": ["candidate-001", "candidate-002"],
            "approval_notes": "Bulk review",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["approved_count"] == 1
    assert body["skipped_count"] == 1
    assert body["error_count"] == 0
    assert (
        repository.get_approval("candidate-001")["approval_status"]
        == "approved"
    )
    assert (
        repository.get_approval("candidate-002")["approval_status"]
        == "rejected"
    )


def test_invalid_review_status_is_rejected_by_api(monkeypatch):
    repository, client = setup_api(monkeypatch)
    repository.ensure_candidate("candidate-001")

    response = client.post(
        "/api/administrator/candidate-approvals/candidate-001/review",
        json={"status": "pending"},
    )

    assert response.status_code == 422
    assert (
        repository.get_approval("candidate-001")["approval_status"]
        == "pending"
    )
