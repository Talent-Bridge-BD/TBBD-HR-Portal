import base64
import json

from starlette.requests import Request

from services.local_auth import _get_easy_auth_principal


def make_request(principal, header_name="TBBD External Candidate"):
    encoded = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("ascii")

    return Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [
            (b"x-ms-client-principal-id", b"external-subject-001"),
            (b"x-ms-client-principal-name", header_name.encode("utf-8")),
            (b"x-ms-client-principal", encoded.encode("ascii")),
        ],
        "query_string": b"",
    })


def test_easy_auth_uses_email_claim_instead_of_display_name():
    request = make_request({
        "claims": [
            {"typ": "name", "val": "TBBD External Candidate"},
            {"typ": "preferred_username", "val": "moazzem900@outlook.com"},
        ]
    })

    principal = _get_easy_auth_principal(request)

    assert principal["id"] == "external-subject-001"
    assert principal["email"] == "moazzem900@outlook.com"
    assert principal["name"] == "TBBD External Candidate"


def test_easy_auth_uses_email_header_as_fallback():
    request = make_request(
        {"claims": [{"typ": "name", "val": "Test Candidate"}]},
        header_name="candidate@example.test",
    )

    principal = _get_easy_auth_principal(request)

    assert principal["email"] == "candidate@example.test"


def test_easy_auth_does_not_use_display_name_as_email():
    request = make_request(
        {"claims": [{"typ": "name", "val": "Test Candidate"}]},
    )

    principal = _get_easy_auth_principal(request)

    assert principal["email"] == ""
    assert principal["id"] == "external-subject-001"


def test_easy_auth_extracts_roles_and_groups_from_claims():
    request = make_request({
        "claims": [
            {"typ": "roles", "val": "Administrator"},
            {"typ": "groups", "val": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"},
            {"typ": "name", "val": "Admin TBBD"},
            {"typ": "preferred_username", "val": "admin@example.test"},
        ]
    })

    principal = _get_easy_auth_principal(request)

    assert principal["roles"] == ["Administrator"]
    assert principal["groups"] == [
        "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"
    ]


def test_easy_auth_preserves_existing_roles_and_groups_without_duplicates():
    request = make_request({
        "roles": ["Administrator"],
        "groups": ["group-001"],
        "claims": [
            {"typ": "roles", "val": "Administrator"},
            {"typ": "roles", "val": "HR Manager"},
            {"typ": "groups", "val": "group-001"},
            {"typ": "groups", "val": "group-002"},
        ]
    })

    principal = _get_easy_auth_principal(request)

    assert principal["roles"] == ["Administrator", "HR Manager"]
    assert principal["groups"] == ["group-001", "group-002"]


def test_easy_auth_returns_none_when_required_headers_are_missing():
    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
    })

    assert _get_easy_auth_principal(request) is None


def test_easy_auth_rejects_malformed_principal():
    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [
            (b"x-ms-client-principal-id", b"external-subject-001"),
            (b"x-ms-client-principal", b"not-valid-base64-json"),
        ],
        "query_string": b"",
    })

    assert _get_easy_auth_principal(request) is None
