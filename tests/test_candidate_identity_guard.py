import pytest
from fastapi import HTTPException
from starlette.requests import Request

from api import candidate as candidate_api


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
def test_external_id_candidate_identity_is_accepted(
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

    assert (
        candidate_api.get_candidate_identity(make_request())
        == "test-external-candidate"
    )


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

    with pytest.raises(HTTPException) as exc:
        candidate_api.get_candidate_identity(make_request())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Candidate role is required"
