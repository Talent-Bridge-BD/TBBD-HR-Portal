import pytest
from fastapi import HTTPException
from starlette.requests import Request

from api import application, hiring, interview


WORKFLOW_APIS = [
    (application, application.get_application_authorization_context),
    (hiring, hiring.get_hiring_authorization_context),
    (interview, interview.get_interview_authorization_context),
]

ROLE_ALIASES = [
    ("Employer.Manager", "Employer Manager"),
    ("HR.Manager", "HR Manager"),
]

DENIED_ROLES = [
    [],
    ["Candidate"],
    ["Candidate.Support"],
    ["Unrecognized.Role"],
]

ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


class FakeOrganizationRepository:
    def get_active_memberships(self, user_id):
        return []


def make_request():
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 12345),
        "scheme": "http",
    })


@pytest.mark.parametrize(
    "module,context_getter",
    WORKFLOW_APIS,
    ids=["application", "hiring", "interview"],
)
@pytest.mark.parametrize(
    "token_role,expected_role",
    ROLE_ALIASES,
    ids=["employer-manager-alias", "hr-manager-alias"],
)
def test_workflow_apis_normalize_supported_role_aliases(
    monkeypatch,
    module,
    context_getter,
    token_role,
    expected_role,
):
    monkeypatch.setattr(
        module,
        "get_request_principal",
        lambda request: {
            "id": "user-001",
            "claims": [
                {"typ": "roles", "val": token_role},
            ],
        },
    )
    monkeypatch.setattr(
        module,
        "_organization_repository",
        FakeOrganizationRepository(),
    )

    context = context_getter(make_request())

    assert context.user_id == "user-001"
    assert context.roles == frozenset({expected_role})
    assert context.organization_ids == frozenset()
    assert context.is_global_administrator is False


@pytest.mark.parametrize(
    "module,context_getter",
    WORKFLOW_APIS,
    ids=["application", "hiring", "interview"],
)
@pytest.mark.parametrize(
    "token_roles",
    DENIED_ROLES,
    ids=[
        "missing-role",
        "candidate-role",
        "candidate-support-role",
        "unsupported-role",
    ],
)
def test_workflow_apis_reject_missing_or_unsupported_roles(
    monkeypatch,
    module,
    context_getter,
    token_roles,
):
    claims = [
        {"typ": "roles", "val": role}
        for role in token_roles
    ]

    monkeypatch.setattr(
        module,
        "get_request_principal",
        lambda request: {
            "id": "user-002",
            "claims": claims,
        },
    )
    monkeypatch.setattr(
        module,
        "_organization_repository",
        FakeOrganizationRepository(),
    )

    with pytest.raises(HTTPException) as exc_info:
        context_getter(make_request())

    assert exc_info.value.status_code == 403


@pytest.mark.parametrize(
    "module,context_getter",
    WORKFLOW_APIS,
    ids=["application", "hiring", "interview"],
)
def test_workflow_apis_preserve_administrator_group_mapping(
    monkeypatch,
    module,
    context_getter,
):
    monkeypatch.setattr(
        module,
        "get_request_principal",
        lambda request: {
            "id": "admin-001",
            "claims": [
                {"typ": "groups", "val": ADMINISTRATOR_GROUP_ID},
            ],
        },
    )
    monkeypatch.setattr(
        module,
        "_organization_repository",
        FakeOrganizationRepository(),
    )

    context = context_getter(make_request())

    assert context.roles == frozenset({"Administrator"})
    assert context.is_global_administrator is True
    assert context.organization_ids == frozenset()
