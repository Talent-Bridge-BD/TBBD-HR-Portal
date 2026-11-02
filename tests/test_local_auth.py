import base64
import json

import pytest
from fastapi import HTTPException
from starlette.requests import Request

import services.local_auth as local_auth
from api import job_compensation


def make_request(headers=None):
    encoded_headers = [
        (key.lower().encode(), value.encode())
        for key, value in (headers or {}).items()
    ]

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "https",
        "path": "/test",
        "raw_path": b"/test",
        "query_string": b"",
        "headers": encoded_headers,
        "server": ("testserver", 443),
        "client": ("testclient", 12345),
    }
    return Request(scope)


def easy_auth_headers():
    principal = {
        "claims": [
            {"typ": "tid", "val": "candidate-tenant"},
            {"typ": "name", "val": "Candidate User"},
        ]
    }
    encoded = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("ascii")

    return {
        "X-MS-CLIENT-PRINCIPAL-ID": "candidate-user-id",
        "X-MS-CLIENT-PRINCIPAL": encoded,
        "X-MS-CLIENT-PRINCIPAL-NAME": "candidate@example.test",
    }



def test_easy_auth_prefers_preferred_username_over_display_name():
    principal = {
        "claims": [
            {"typ": "tid", "val": "candidate-tenant"},
            {"typ": "name", "val": "TBBD External Candidate"},
            {"typ": "preferred_username", "val": "moazzem900@outlook.com"},
        ]
    }
    encoded = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("ascii")
    headers = {
        "X-MS-CLIENT-PRINCIPAL-ID": "candidate-user-id",
        "X-MS-CLIENT-PRINCIPAL": encoded,
        "X-MS-CLIENT-PRINCIPAL-NAME": "TBBD External Candidate",
    }

    result = local_auth._get_easy_auth_principal(make_request(headers))

    assert result["email"] == "moazzem900@outlook.com"
    assert result["name"] == "TBBD External Candidate"
    assert result["id"] == "candidate-user-id"


def test_easy_auth_does_not_treat_display_name_as_email():
    principal = {
        "claims": [
            {"typ": "tid", "val": "candidate-tenant"},
            {"typ": "name", "val": "TBBD External Candidate"},
        ]
    }
    encoded = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("ascii")
    headers = {
        "X-MS-CLIENT-PRINCIPAL-ID": "candidate-user-id",
        "X-MS-CLIENT-PRINCIPAL": encoded,
        "X-MS-CLIENT-PRINCIPAL-NAME": "TBBD External Candidate",
    }

    result = local_auth._get_easy_auth_principal(make_request(headers))

    assert result["email"] is None
    assert result["name"] == "TBBD External Candidate"


def test_valid_bearer_takes_precedence_over_easy_auth(monkeypatch):
    workforce_principal = {
        "id": "workforce-user-id",
        "email": "staff@example.test",
    }

    monkeypatch.setattr(
        local_auth,
        "_get_entra_principal",
        lambda request: workforce_principal,
    )

    def unexpected_easy_auth_call(request):
        pytest.fail("Easy Auth must not override a supplied Bearer token")

    monkeypatch.setattr(
        local_auth,
        "_get_easy_auth_principal",
        unexpected_easy_auth_call,
    )

    headers = {
        **easy_auth_headers(),
        "Authorization": "Bearer workforce-token",
    }

    assert local_auth.get_request_principal(make_request(headers)) == (
        workforce_principal
    )


def test_invalid_bearer_never_falls_back_to_easy_auth(monkeypatch):
    monkeypatch.setattr(
        local_auth,
        "_get_entra_principal",
        lambda request: None,
    )

    def unexpected_easy_auth_call(request):
        pytest.fail("Invalid Bearer token must not fall back to Easy Auth")

    monkeypatch.setattr(
        local_auth,
        "_get_easy_auth_principal",
        unexpected_easy_auth_call,
    )

    headers = {
        **easy_auth_headers(),
        "Authorization": "Bearer invalid-token",
    }

    assert local_auth.get_request_principal(make_request(headers)) is None


@pytest.mark.parametrize(
    "authorization",
    [
        "Bearer",
        "Bearer   ",
        "Basic credentials",
        "InvalidHeader",
    ],
)
def test_malformed_or_unsupported_authorization_never_falls_back(
    monkeypatch,
    authorization,
):
    def unexpected_easy_auth_call(request):
        pytest.fail("Authorization header must prevent cookie fallback")

    monkeypatch.setattr(
        local_auth,
        "_get_easy_auth_principal",
        unexpected_easy_auth_call,
    )

    request = make_request({
        **easy_auth_headers(),
        "Authorization": authorization,
    })

    assert local_auth.get_request_principal(request) is None


def test_easy_auth_is_used_when_authorization_header_is_absent(monkeypatch):
    candidate_principal = {
        "id": "candidate-user-id",
        "email": "candidate@example.test",
    }

    monkeypatch.setattr(
        local_auth,
        "_get_easy_auth_principal",
        lambda request: candidate_principal,
    )

    def unexpected_bearer_call(request):
        pytest.fail("No Bearer token was supplied")

    monkeypatch.setattr(
        local_auth,
        "_get_entra_principal",
        unexpected_bearer_call,
    )

    assert local_auth.get_request_principal(
        make_request(easy_auth_headers())
    ) == candidate_principal


def test_no_credentials_returns_no_principal(monkeypatch):
    monkeypatch.setattr(
        local_auth,
        "_get_easy_auth_principal",
        lambda request: None,
    )

    assert local_auth.get_request_principal(make_request()) is None


def test_job_compensation_uses_shared_principal_resolver(monkeypatch):
    workforce_principal = {
        "id": "workforce-user-id",
        "claims": [
            {
                "typ": "groups",
                "val": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66",
            },
        ],
    }

    membership_lookup = []

    monkeypatch.setattr(
        job_compensation,
        "get_request_principal",
        lambda request: workforce_principal,
    )
    monkeypatch.setattr(
        job_compensation._organization_repository,
        "get_active_memberships",
        lambda user_id: membership_lookup.append(user_id) or [],
    )

    context = job_compensation.get_job_compensation_authorization_context(
        make_request({"Authorization": "Bearer workforce-token"})
    )

    assert "Administrator" in context.roles
    assert membership_lookup == ["workforce-user-id"]


def test_job_compensation_rejects_missing_shared_principal(monkeypatch):
    monkeypatch.setattr(
        job_compensation,
        "get_request_principal",
        lambda request: None,
    )

    with pytest.raises(HTTPException) as exc:
        job_compensation.get_job_compensation_authorization_context(
            make_request()
        )

    assert exc.value.status_code == 401
