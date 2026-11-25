from services.authorization import build_authorization_context
import main
import services.local_auth as local_auth
from types import SimpleNamespace
import json
import base64
from fastapi.testclient import TestClient
from api import candidate as candidate_api
from repositories.application_roles import InMemoryApplicationRoleRepository
from repositories.candidate_approvals import InMemoryCandidateApprovalRepository
from models.user_profile import UserProfile

client = TestClient(main.app)

CANDIDATE_TENANT_ID = "c8573333-aad0-4a28-8e40-c20e17989f61"
ADMIN_GROUP_ID = "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"


def get_me_with_principal(monkeypatch, principal, approved_candidate=False):
    roles = InMemoryApplicationRoleRepository()
    approvals = InMemoryCandidateApprovalRepository()
    monkeypatch.setattr(candidate_api, "_application_role_repository", roles)
    monkeypatch.setattr(candidate_api, "_approval_repository", approvals)

    user_id = principal.get("application_user_id", principal["id"])
    email = principal.get("email", "")

    monkeypatch.setattr(
        main._user_profile_repository,
        "get_by_email",
        lambda requested_email: (
            UserProfile(user_id=user_id, primary_email=requested_email)
            if requested_email
            and requested_email.casefold() == email.casefold()
            else None
        ),
    )

    if approved_candidate:
        approvals.ensure_candidate(user_id)
        approvals.review_candidate(
            user_id,
            status="approved",
            reviewed_by="test-admin",
            approval_notes=None,
        )
        roles.grant_role(user_id, "Candidate", assigned_by="test-admin")
    elif principal.get("assign_candidate_role"):
        roles.grant_role(user_id, "Candidate", assigned_by="test-admin")
    elif principal.get("assign_candidate_role_to_principal"):
        roles.grant_role(
            principal["id"],
            "Candidate",
            assigned_by="test-admin",
        )

    monkeypatch.setattr(
        main,
        "get_request_principal",
        lambda request: principal,
    )
    monkeypatch.setattr(
        main._organization_repository,
        "get_active_memberships",
        lambda user_id: [],
    )
    return client.get("/api/me")


def test_api_me_uses_easy_auth_email_claim_and_preserves_display_name(monkeypatch):
    principal_id = "integration-candidate-id"
    expected_email = "moazzem900@outlook.com"
    display_name = "TBBD External Candidate"

    claims = {
        "auth_typ": "aad",
        "claims": [
            {"typ": "tid", "val": CANDIDATE_TENANT_ID},
            {"typ": "name", "val": display_name},
            {"typ": "preferred_username", "val": expected_email},
        ],
    }
    encoded_principal = base64.b64encode(
        json.dumps(claims).encode("utf-8")
    ).decode("ascii")

    headers = {
        "X-MS-CLIENT-PRINCIPAL-ID": principal_id,
        "X-MS-CLIENT-PRINCIPAL-NAME": display_name,
        "X-MS-CLIENT-PRINCIPAL": encoded_principal,
    }

    monkeypatch.setattr(
        main,
        "get_request_principal",
        lambda request: local_auth._get_easy_auth_principal(request),
    )

    profile_lookups = []
    monkeypatch.setattr(
        main._user_profile_repository,
        "get_by_email",
        lambda email: profile_lookups.append(email) or None,
    )

    monkeypatch.setattr(
        candidate_api,
        "_application_role_repository",
        SimpleNamespace(
            has_role=lambda user_id, role: (
                user_id == principal_id and role == "Candidate"
            )
        ),
    )

    monkeypatch.setattr(
        main._organization_repository,
        "get_active_memberships",
        lambda user_id: [],
    )

    response = client.get("/api/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["user"]["email"] == expected_email
    assert data["user"]["name"] == display_name
    assert data["user"]["id"] == principal_id
    assert "Candidate" in data["roles"]
    assert profile_lookups == [expected_email]


def test_external_id_candidate_receives_role_only_when_approved(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-candidate",
            "email": "candidate@example.test",
            "name": "Test Candidate",
            "tenant_id": CANDIDATE_TENANT_ID,
            "claims": [
                {"typ": "tid", "val": CANDIDATE_TENANT_ID},
            ],
        },
        approved_candidate=True,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "Candidate" in data["roles"]
    assert "Employee" not in data["roles"]


def test_external_id_candidate_with_role_receives_role_while_pending(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-pending-assigned-candidate",
            "email": "pending@example.test",
            "tenant_id": CANDIDATE_TENANT_ID,
            "claims": [{"typ": "tid", "val": CANDIDATE_TENANT_ID}],
            "assign_candidate_role": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "Candidate" in data["roles"]
    assert "Employee" not in data["roles"]


def test_external_id_candidate_without_role_is_not_candidate(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-pending-candidate",
            "email": "pending@example.test",
            "tenant_id": CANDIDATE_TENANT_ID,
            "claims": [{"typ": "tid", "val": CANDIDATE_TENANT_ID}],
        },
    )

    assert response.status_code == 200
    assert "Candidate" not in response.json()["roles"]
    assert "Employee" not in response.json()["roles"]



def test_external_id_candidate_role_uses_principal_id_when_profile_id_differs(
    monkeypatch,
):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "external-principal-id",
            "application_user_id": "canonical-profile-id",
            "email": "candidate-mismatch@example.test",
            "tenant_id": CANDIDATE_TENANT_ID,
            "claims": [{"typ": "tid", "val": CANDIDATE_TENANT_ID}],
            "assign_candidate_role_to_principal": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == "canonical-profile-id"
    assert "Candidate" in data["roles"]
    assert "Employee" not in data["roles"]

def test_workforce_administrator_role_is_preserved(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-admin",
            "email": "admin@example.test",
            "name": "Test Administrator",
            "claims": [
                {"typ": "groups", "val": ADMIN_GROUP_ID},
            ],
        },
    )

    assert response.status_code == 200
    assert "Administrator" in response.json()["roles"]


def test_workforce_user_keeps_employee_default(monkeypatch):
    response = get_me_with_principal(
        monkeypatch,
        {
            "id": "test-employee",
            "email": "employee@example.test",
            "name": "Test Employee",
            "claims": [],
        },
    )

    assert response.status_code == 200
    assert "Employee" in response.json()["roles"]
    assert "Candidate" not in response.json()["roles"]


def test_easy_auth_principal_exposes_roles_and_groups():
    import base64
    import json

    from starlette.requests import Request
    from services import local_auth

    claims = [
        {"typ": "groups", "val": "administrator-group-id"},
        {"typ": "roles", "val": "Administrator"},
        {"typ": "http://schemas.microsoft.com/ws/2008/06/identity/claims/role",
         "val": "HR Manager"},
        {"typ": "name", "val": "Test Administrator"},
        {"typ": "malformed"},
        None,
    ]
    encoded = base64.b64encode(
        json.dumps({"claims": claims}).encode("utf-8")
    ).decode("ascii")

    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [
            (b"x-ms-client-principal-id", b"test-user-id"),
            (b"x-ms-client-principal", encoded.encode("ascii")),
        ],
    })

    principal = local_auth._get_easy_auth_principal(request)

    assert principal is not None
    assert principal["groups"] == ["administrator-group-id"]
    assert principal["roles"] == ["Administrator", "HR Manager"]
    assert principal["claims"] == claims
    assert principal["id"] == "test-user-id"
    assert principal["name"] == "Test Administrator"


def test_employer_external_identity_uses_mapping_across_main_routes(monkeypatch):
    canonical_user_id = "canonical-existing-user"
    external_object_id = "new-employer-external-object-id"
    organization_id = "existing-org"
    membership_lookups = []

    principal = {
        "id": external_object_id,
        "object_id": external_object_id,
        "tenant_id": local_auth.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        "email": "employer.manager@loyaltrademanagement.com",
        "name": "Employer Manager",
        "claims": [
            {
                "typ": "groups",
                "val": "2f2e6a59-1e61-4467-8642-3a76cf8aa8d1",
            },
        ],
    }

    class FakeMappingRepository:
        def get_mapping(self, **kwargs):
            assert kwargs["provider"] == (
                local_auth.TBBD_EMPLOYER_EXTERNAL_ID_PROVIDER
            )
            assert kwargs["tenant_id"] == (
                local_auth.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID
            )
            assert kwargs["external_object_id"] == external_object_id
            return {
                "application_user_id": canonical_user_id,
                "status": "Active",
            }

    membership = SimpleNamespace(
        user_id=canonical_user_id,
        organization_id=organization_id,
        role="Employer Manager",
        status="active",
    )
    organization = SimpleNamespace(
        id=organization_id,
        name="Existing Organization",
        status="active",
    )

    monkeypatch.setattr(
        main, "get_request_principal", lambda request: principal
    )
    monkeypatch.setattr(
        main,
        "is_employer_external_principal",
        lambda value: value is principal,
    )
    monkeypatch.setattr(
        main, "_identity_mapping_repository", FakeMappingRepository()
    )
    monkeypatch.setattr(
        main._user_profile_repository,
        "get_by_email",
        lambda email: (_ for _ in ()).throw(
            AssertionError("Employer mapping must take precedence over email lookup")
        ),
    )
    monkeypatch.setattr(
        main._organization_repository,
        "get_active_memberships",
        lambda user_id: (
            membership_lookups.append(user_id) or [membership]
        ),
    )
    monkeypatch.setattr(
        main._organization_repository,
        "list_active_organizations",
        lambda: [organization],
    )
    monkeypatch.setattr(
        main._organization_repository,
        "list_members",
        lambda requested_org_id: [membership],
    )

    me = client.get("/api/me")
    assert me.status_code == 200, me.text
    assert me.json()["user"]["id"] == canonical_user_id
    assert "Employer Manager" in me.json()["roles"]
    assert organization_id in me.json()["organization_ids"]

    organizations = client.get("/api/organizations")
    assert organizations.status_code == 200, organizations.text
    assert organizations.json()["organizations"][0]["id"] == organization_id

    detail = client.get(f"/api/organizations/{organization_id}")
    assert detail.status_code == 200, detail.text

    assert membership_lookups == [canonical_user_id] * 3


def test_unmapped_employer_external_identity_is_rejected_across_main_routes(
    monkeypatch,
):
    external_object_id = "unmapped-employer-external-object-id"

    principal = {
        "id": external_object_id,
        "object_id": external_object_id,
        "tenant_id": local_auth.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        "email": "unmapped-employer@example.com",
        "name": "Unmapped Employer",
        "claims": [
            {
                "typ": "groups",
                "val": "2f2e6a59-1e61-4467-8642-3a76cf8aa8d1",
            },
        ],
    }

    class MissingMappingRepository:
        def get_mapping(self, **kwargs):
            return None

    monkeypatch.setattr(
        main, "get_request_principal", lambda request: principal
    )
    monkeypatch.setattr(
        main,
        "is_employer_external_principal",
        lambda value: value is principal,
    )
    monkeypatch.setattr(
        main, "_identity_mapping_repository", MissingMappingRepository()
    )

    responses = [
        client.get("/api/me"),
        client.get("/api/organizations"),
        client.get("/api/organizations/existing-org"),
    ]

    assert [response.status_code for response in responses] == [
        403, 403, 403
    ]


def test_employer_external_identity_rejects_revoked_mapping_in_api_me(
    monkeypatch,
):
    external_object_id = "revoked-employer-external-object-id"
    principal = {
        "id": external_object_id,
        "object_id": external_object_id,
        "tenant_id": local_auth.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        "email": "employer.manager@loyaltrademanagement.com",
        "claims": [
            {
                "typ": "groups",
                "val": "2f2e6a59-1e61-4467-8642-3a76cf8aa8d1",
            },
        ],
    }

    class RevokedMappingRepository:
        def get_mapping(self, **kwargs):
            return {
                "application_user_id": "canonical-existing-user",
                "status": "Revoked",
            }

    monkeypatch.setattr(
        main, "get_request_principal", lambda request: principal
    )
    monkeypatch.setattr(
        main,
        "is_employer_external_principal",
        lambda value: value is principal,
    )
    monkeypatch.setattr(
        main, "_identity_mapping_repository", RevokedMappingRepository()
    )

    response = client.get("/api/me")
    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Employer external identity mapping is not active"
    )


def test_membership_cannot_grant_candidate_or_global_administrator():
    memberships = [
        SimpleNamespace(
            user_id="existing-user",
            organization_id="org-1",
            role="Candidate",
            status="active",
        ),
        SimpleNamespace(
            user_id="existing-user",
            organization_id="org-2",
            role="Administrator",
            status="active",
        ),
    ]

    context = build_authorization_context(
        user_id="existing-user",
        roles=[],
        memberships=memberships,
    )

    assert "Candidate" not in context.roles
    assert "Administrator" not in context.roles
    assert context.is_global_administrator is False


def test_active_employer_membership_grants_employer_manager_role():
    membership = SimpleNamespace(
        user_id="existing-user",
        organization_id="org-1",
        role="Employer Manager",
        status="active",
    )

    context = build_authorization_context(
        user_id="existing-user",
        roles=[],
        memberships=[membership],
    )

    assert "Employer Manager" in context.roles
    assert context.organization_ids == frozenset({"org-1"})
    assert context.is_global_administrator is False


def test_inactive_employer_membership_grants_no_role_or_access():
    membership = SimpleNamespace(
        user_id="existing-user",
        organization_id="org-1",
        role="Employer Manager",
        status="inactive",
    )

    context = build_authorization_context(
        user_id="existing-user",
        roles=[],
        memberships=[membership],
    )

    assert "Employer Manager" not in context.roles
    assert not context.organization_ids
