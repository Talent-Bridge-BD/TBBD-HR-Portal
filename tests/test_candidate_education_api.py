from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from main import app
from api import candidate as candidate_api


class FakeApprovalRepository:
    def __init__(self, status="pending"):
        self.status = status

    def ensure_candidate(self, principal_id):
        return {"approval_status": self.status}


class FakeEducationService:
    def __init__(self):
        self.records = []
        self.calls = []

    def list_education(self, candidate_id):
        self.calls.append(("list", candidate_id))
        return list(self.records)

    def create_education(
        self, candidate_id, degree_qualification, institution,
        field_of_study, start_date, end_date, description
    ):
        self.calls.append((
            "create", candidate_id, degree_qualification, institution,
            field_of_study, start_date, end_date, description
        ))
        return make_education(
            candidate_id=candidate_id,
            degree_qualification=degree_qualification or "",
            institution=institution or "",
            field_of_study=field_of_study,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

    def update_education(
        self, candidate_id, education_id, degree_qualification,
        institution, field_of_study, start_date, end_date, description
    ):
        self.calls.append((
            "update", candidate_id, education_id, degree_qualification,
            institution, field_of_study, start_date, end_date, description
        ))
        if education_id == "missing-or-not-owned":
            return None
        return make_education(
            education_id=education_id,
            candidate_id=candidate_id,
            degree_qualification=degree_qualification or "",
            institution=institution or "",
            field_of_study=field_of_study,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

    def delete_education(self, candidate_id, education_id):
        self.calls.append(("delete", candidate_id, education_id))
        return education_id == "education-owned"


def make_education(
    education_id="education-owned",
    candidate_id="candidate-001",
    degree_qualification="",
    institution="",
    field_of_study=None,
    start_date=None,
    end_date=None,
    description=None,
):
    return SimpleNamespace(
        id=education_id,
        candidate_id=candidate_id,
        degree_qualification=degree_qualification,
        institution=institution,
        field_of_study=field_of_study,
        start_date=start_date,
        end_date=end_date,
        description=description,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )


@pytest.fixture
def api_setup(monkeypatch):
    service = FakeEducationService()
    approval = FakeApprovalRepository("pending")

    monkeypatch.setattr(candidate_api, "_education_service", service)
    monkeypatch.setattr(candidate_api, "_approval_repository", approval)
    monkeypatch.setattr(
        candidate_api,
        "get_request_principal",
        lambda request: {
            "id": "candidate-001",
            "claims": [{"typ": "roles", "val": "Candidate"}],
        },
    )

    return TestClient(app), service, approval


def test_get_education_lists_candidate_records(api_setup):
    client, service, _ = api_setup
    service.records = [make_education()]

    response = client.get("/api/candidate/education")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "education-owned"
    assert service.calls == [("list", "candidate-001")]


def test_post_education_rejects_all_fields_omitted(api_setup):
    client, service, _ = api_setup

    response = client.post(
        "/api/candidate/education",
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Provide at least one education detail"
    assert service.calls == []

def test_post_education_rejects_end_date_before_start_date(api_setup):
    client, service, _ = api_setup

    response = client.post(
        "/api/candidate/education",
        json={
            "start_date": "2024-01-01",
            "end_date": "2020-01-01",
        },
    )

    assert response.status_code == 400
    assert "End date cannot be before start date" in response.json()["detail"]
    assert service.calls == []


def test_put_education_updates_owned_record(api_setup):
    client, service, _ = api_setup

    response = client.put(
        "/api/candidate/education/education-owned",
        json={
            "degree_qualification": "Diploma",
            "institution": "Example Institute",
            "field_of_study": "Engineering",
        },
    )

    assert response.status_code == 200
    assert response.json()["degree_qualification"] == "Diploma"
    assert service.calls[0][0:3] == (
        "update", "candidate-001", "education-owned"
    )


def test_put_education_returns_404_for_unavailable_record(api_setup):
    client, service, _ = api_setup

    response = client.put(
        "/api/candidate/education/missing-or-not-owned",
        json={},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Education record not found"


def test_delete_education_deletes_owned_record(api_setup):
    client, service, _ = api_setup

    response = client.delete(
        "/api/candidate/education/education-owned"
    )

    assert response.status_code == 204
    assert service.calls == [
        ("delete", "candidate-001", "education-owned")
    ]


def test_delete_education_returns_404_for_unavailable_record(api_setup):
    client, service, _ = api_setup

    response = client.delete(
        "/api/candidate/education/missing-or-not-owned"
    )

    assert response.status_code == 404


def test_pending_candidate_cannot_create_application(api_setup):
    client, service, approval = api_setup
    approval.status = "pending"

    response = client.post(
        "/api/candidate/applications",
        json={"job_id": "test-job"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Candidate account is awaiting administrator approval"
    )
    assert service.calls == []

def test_pending_candidate_can_access_education_profile(api_setup):
    client, _, approval = api_setup
    approval.status = "pending"

    response = client.get("/api/candidate/education")

    assert response.status_code == 200


def test_rejected_candidate_cannot_access_education(api_setup):
    client, service, approval = api_setup
    approval.status = "rejected"

    response = client.get("/api/candidate/education")

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Candidate account has not been approved"
    )
    assert service.calls == []


def test_user_without_candidate_role_cannot_access_education(api_setup, monkeypatch):
    client, service, _ = api_setup
    monkeypatch.setattr(
        candidate_api,
        "get_request_principal",
        lambda request: {
            "id": "unrelated-user",
            "claims": [],
        },
    )

    response = client.get("/api/candidate/education")

    assert response.status_code == 403
    assert response.json()["detail"] == "Candidate role is required"
    assert service.calls == []
