from fastapi import HTTPException

from api import application as api


class FakeProfile:
    def __init__(self, user_id):
        self.user_id = user_id


class FakeProfileRepository:
    def __init__(self, profile):
        self.profile = profile
        self.looked_up_email = None

    def get_by_email(self, email):
        self.looked_up_email = email
        return self.profile


class FakeOrganizationRepository:
    def __init__(self):
        self.membership_user_ids = []

    def get_active_memberships(self, user_id):
        self.membership_user_ids.append(user_id)
        return []


class FakeApplicationRoleRepository:
    def __init__(self, result):
        self.result = result
        self.lookups = []

    def has_role(self, user_id, role):
        self.lookups.append((user_id, role))
        return self.result


def setup_application_authorization(monkeypatch, principal, profile, database_admin):
    profile_repository = FakeProfileRepository(profile)
    organization_repository = FakeOrganizationRepository()
    role_repository = FakeApplicationRoleRepository(database_admin)

    monkeypatch.setattr(
        api,
        "get_request_principal",
        lambda request: principal,
    )
    monkeypatch.setattr(
        api,
        "_user_profile_repository",
        profile_repository,
    )
    monkeypatch.setattr(
        api,
        "_organization_repository",
        organization_repository,
    )
    monkeypatch.setattr(
        api,
        "application_role_repository",
        role_repository,
    )

    return profile_repository, organization_repository, role_repository


def test_application_authorization_accepts_database_assigned_administrator(
    monkeypatch,
):
    principal = {
        "id": "entra-object-001",
        "email": "admin@example.test",
        "claims": [],
    }
    application_user_id = "application-user-001"

    profile_repository, organization_repository, role_repository = (
        setup_application_authorization(
            monkeypatch,
            principal,
            FakeProfile(application_user_id),
            True,
        )
    )

    context = api.get_application_authorization_context(None)

    assert profile_repository.looked_up_email == "admin@example.test"
    assert role_repository.lookups == [
        (application_user_id, "Administrator"),
    ]
    assert organization_repository.membership_user_ids == [
        application_user_id,
    ]
    assert context.user_id == application_user_id
    assert api.is_global_administrator(context)


def test_application_authorization_accepts_administrator_token_role(
    monkeypatch,
):
    principal = {
        "id": "entra-object-002",
        "email": "admin@example.test",
        "claims": [
            {"typ": "roles", "val": "Administrator"},
        ],
    }

    profile_repository, organization_repository, role_repository = (
        setup_application_authorization(
            monkeypatch,
            principal,
            None,
            False,
        )
    )

    context = api.get_application_authorization_context(None)

    assert profile_repository.looked_up_email is None
    assert role_repository.lookups == []
    assert organization_repository.membership_user_ids == [
        "entra-object-002",
    ]
    assert context.user_id == "entra-object-002"
    assert api.is_global_administrator(context)


def test_application_authorization_rejects_user_without_allowed_role(
    monkeypatch,
):
    principal = {
        "id": "entra-object-003",
        "email": "user@example.test",
        "claims": [
            {"typ": "roles", "val": "Candidate"},
        ],
    }

    setup_application_authorization(
        monkeypatch,
        principal,
        None,
        False,
    )

    try:
        api.get_application_authorization_context(None)
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == "Employer management role is required"
    else:
        raise AssertionError("Expected an HTTP 403 authorization failure")
