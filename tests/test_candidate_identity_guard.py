import pytest
from fastapi import HTTPException
from starlette.requests import Request

from api import candidate as candidate_api
from repositories.candidate_approvals import (
    InMemoryCandidateApprovalRepository,
)


def make_request():
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/api/candidate/applications",
        "headers": [],
        "query_string": b"",
    })


@pytest.fixture
def approval_repository(monkeypatch):
    repository = InMemoryCandidateApprovalRepository()
    monkeypatch.setattr(candidate_api, "_approval_repository", repository)
    return repository


@pytest.mark.parametrize("identity_signal", [
    {"provider_name": "TBBDCandidateExternalID"},
    {"app_displayname": "TBBD Candidate Portal"},
])
def test_approved_external_id_candidate_is_accepted(
    monkeypatch, approval_repository, identity_signal
):
    principal_id = "test-external-candidate"
    principal = {
        "id": principal_id,
        "tenant_id": "unrelated-tenant",
        "claims": [],
        **identity_signal,
    }
    monkeypatch.setattr(
        candidate_api, "get_request_principal", lambda request: principal
    )

    approval_repository.ensure_candidate(principal_id)
    approval_repository.review_candidate(
        principal_id, status="approved", reviewed_by="admin-test"
    )

    assert candidate_api.get_candidate_identity(make_request()) == principal_id


def test_pending_external_id_candidate_is_blocked(
    monkeypatch, approval_repository
):
    principal = {
        "id": "test-pending-candidate",
        "tenant_id": "unrelated-tenant",
        "claims": [],
        "provider_name": "TBBDCandidateExternalID",
    }
    monkeypatch.setattr(
        candidate_api, "get_request_principal", lambda request: principal
    )
    approval_repository.ensure_candidate(principal["id"])

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Candidate account is awaiting administrator approval"
    )


def test_rejected_external_id_candidate_is_blocked(
    monkeypatch, approval_repository
):
    principal = {
        "id": "test-rejected-candidate",
        "tenant_id": "unrelated-tenant",
        "claims": [],
        "provider_name": "TBBDCandidateExternalID",
    }
    monkeypatch.setattr(
        candidate_api, "get_request_principal", lambda request: principal
    )
    approval_repository.ensure_candidate(principal["id"])
    approval_repository.review_candidate(
        principal["id"], status="rejected", reviewed_by="admin-test"
    )

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate account has not been approved"


def test_unrecognized_identity_is_rejected(
    monkeypatch, approval_repository
):
    principal = {
        "id": "test-unrelated-user",
        "tenant_id": "unrelated-tenant",
        "claims": [],
    }
    monkeypatch.setattr(
        candidate_api, "get_request_principal", lambda request: principal
    )

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate role is required"
