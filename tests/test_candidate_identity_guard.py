import pytest
from fastapi import HTTPException
from starlette.requests import Request

from api import candidate as candidate_api
from repositories.application_roles import InMemoryApplicationRoleRepository


def make_request():
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/api/candidate/applications",
        "headers": [],
        "query_string": b"",
    })


@pytest.mark.parametrize(
    "identity_signal",
    [
        {"provider_name": "TBBDCandidateExternalID"},
        {"app_displayname": "TBBD Candidate Portal"},
    ],
)
def test_external_id_identifies_onboarding_but_does_not_grant_role(
    monkeypatch, identity_signal
):
    principal = {
        "id": "test-external-candidate",
        "tenant_id": "unrelated-tenant",
        "claims": [],
        **identity_signal,
    }
    monkeypatch.setattr(
        candidate_api,
        "get_request_principal",
        lambda request: principal,
    )
    monkeypatch.setattr(
        candidate_api,
        "_application_role_repository",
        InMemoryApplicationRoleRepository(),
    )

    assert candidate_api._candidate_onboarding_identity(make_request()) == "test-external-candidate"
    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())
    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate role is required"


def test_unrecognized_identity_is_rejected(monkeypatch):
    principal = {
        "id": "test-unrelated-user",
        "tenant_id": "unrelated-tenant",
        "claims": [],
    }
    monkeypatch.setattr(
        candidate_api,
        "get_request_principal",
        lambda request: principal,
    )
    monkeypatch.setattr(
        candidate_api,
        "_application_role_repository",
        InMemoryApplicationRoleRepository(),
    )

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate identity or role is required"


def test_revoked_candidate_role_blocks_profile_access(monkeypatch):
    principal = {
        "id": "revoked-external-candidate",
        "tenant_id": "unrelated-tenant",
        "provider_name": "TBBDCandidateExternalID",
        "claims": [],
    }
    roles = InMemoryApplicationRoleRepository()
    roles.grant_role(principal["id"], "Candidate", assigned_by="test-admin")
    roles.revoke_role(principal["id"], "Candidate", assigned_by="test-admin")

    monkeypatch.setattr(
        candidate_api, "get_request_principal", lambda request: principal
    )
    monkeypatch.setattr(candidate_api, "_application_role_repository", roles)

    with pytest.raises(HTTPException) as exc:
        candidate_api.require_candidate_profile_access(make_request())

    assert exc.value.status_code == 403
    assert "Candidate access is currently inactive" in exc.value.detail
    assert "contact the TBBD HR team" in exc.value.detail
