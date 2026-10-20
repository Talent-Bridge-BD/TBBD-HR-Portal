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
        "path": "/api/candidate/profile",
        "headers": [],
        "query_string": b"",
    })


@pytest.fixture
def approval_repository(monkeypatch):
    repository = InMemoryCandidateApprovalRepository()
    monkeypatch.setattr(candidate_api, "_approval_repository", repository)
    return repository


def set_principal(monkeypatch, principal):
    monkeypatch.setattr(
        candidate_api, "get_request_principal", lambda request: principal
    )


def candidate_principal(principal_id, **extra):
    return {
        "id": principal_id,
        "claims": [{"typ": "roles", "val": "Candidate"}],
        **extra,
    }


@pytest.mark.parametrize("identity_signal", [
    {"provider_name": "TBBDCandidateExternalID"},
    {"app_displayname": "TBBD Candidate Portal"},
])
def test_external_id_signal_alone_does_not_grant_candidate_role(
    monkeypatch, approval_repository, identity_signal
):
    principal = {
        "id": "test-external-without-role",
        "claims": [],
        **identity_signal,
    }
    set_principal(monkeypatch, principal)

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate role is required"


def test_approved_candidate_role_is_accepted(
    monkeypatch, approval_repository
):
    principal_id = "test-approved-candidate"
    set_principal(monkeypatch, candidate_principal(principal_id))
    approval_repository.ensure_candidate(principal_id)
    approval_repository.review_candidate(
        principal_id, status="approved", reviewed_by="admin-test"
    )

    assert candidate_api.get_candidate_identity(make_request()) == principal_id
    assert (
        candidate_api.get_approved_candidate_identity(make_request())
        == principal_id
    )


def test_pending_candidate_can_access_profile_but_not_approved_features(
    monkeypatch, approval_repository
):
    principal_id = "test-pending-candidate"
    set_principal(
        monkeypatch,
        candidate_principal(
            principal_id,
            provider_name="TBBDCandidateExternalID",
        ),
    )
    approval_repository.ensure_candidate(principal_id)

    assert candidate_api.get_candidate_identity(make_request()) == principal_id

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_approved_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Candidate account is awaiting administrator approval"
    )


def test_rejected_candidate_is_blocked(
    monkeypatch, approval_repository
):
    principal_id = "test-rejected-candidate"
    set_principal(monkeypatch, candidate_principal(principal_id))
    approval_repository.ensure_candidate(principal_id)
    approval_repository.review_candidate(
        principal_id, status="rejected", reviewed_by="admin-test"
    )

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate account has not been approved"


def test_unrecognized_identity_is_rejected(
    monkeypatch, approval_repository
):
    set_principal(
        monkeypatch,
        {"id": "test-unrelated-user", "claims": []},
    )

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate role is required"
