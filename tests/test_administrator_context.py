import base64
import json
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from fastapi.testclient import TestClient

from api import administrator
from main import app


ADMIN_GROUP_ID = "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"


class FakeOrganizationRepository:
    def get_active_memberships(self, user_id):
        return []

    def list_active_organizations(self):
        return []


def make_request(claims):
    encoded = base64.b64encode(
        json.dumps({"claims": claims}).encode("utf-8")
    ).decode("ascii")

    return Request({
        "type": "http",
        "method": "GET",
        "path": "/api/administrator/dashboard",
        "headers": [
            (b"x-ms-client-principal-id", b"test-admin-001"),
            (b"x-ms-client-principal", encoded.encode("ascii")),
        ],
        "query_string": b"",
    })


@pytest.fixture
def fake_organization_repository(monkeypatch):
    repository = FakeOrganizationRepository()
    monkeypatch.setattr(
        administrator,
        "_organization_repository",
        repository,
    )
    return repository


def test_administrator_context_accepts_role_from_easy_auth_claims(
    monkeypatch,
    fake_organization_repository,
):
    request = make_request([
        {"typ": "roles", "val": "Administrator"},
    ])

    context = administrator._get_administrator_context(request)

    assert context.user_id == "test-admin-001"
    assert context.is_global_administrator is True
    assert "Administrator" in context.roles


def test_administrator_context_accepts_configured_admin_group(
    monkeypatch,
    fake_organization_repository,
):
    request = make_request([
        {"typ": "groups", "val": ADMIN_GROUP_ID},
    ])

    context = administrator._get_administrator_context(request)

    assert context.is_global_administrator is True
    assert "Administrator" in context.roles


def test_administrator_context_denies_user_without_admin_role_or_group(
    monkeypatch,
    fake_organization_repository,
):
    request = make_request([
        {"typ": "name", "val": "Ordinary User"},
        {"typ": "preferred_username", "val": "user@example.test"},
    ])

    with pytest.raises(HTTPException) as exc_info:
        administrator._get_administrator_context(request)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Administrator access required"


def test_administrator_context_requires_authenticated_principal(
    monkeypatch,
    fake_organization_repository,
):
    monkeypatch.setattr(
        administrator,
        "get_request_principal",
        lambda request: None,
    )

    request = make_request([])

    with pytest.raises(HTTPException) as exc_info:
        administrator._get_administrator_context(request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authenticated user required"

def test_administrator_dashboard_endpoint_accepts_top_level_role(
    fake_organization_repository,
):
    principal = {
        "roles": ["Administrator"],
        "claims": [],
    }

    encoded_principal = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("ascii")

    headers = {
        "X-MS-CLIENT-PRINCIPAL-ID": "test-admin-001",
        "X-MS-CLIENT-PRINCIPAL": encoded_principal,
    }

    response = TestClient(app).get(
        "/api/administrator/dashboard",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["organizations"]["active"] == 0
    assert response.json()["roles"]["total"] == len(
        administrator.AUTHORIZATION_GROUPS
    )
