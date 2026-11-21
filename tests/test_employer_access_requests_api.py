from fastapi.testclient import TestClient
from fastapi import HTTPException

from main import app


BASE = "/api/employer-access-requests"

VALID_REQUEST = {
    "company_name": "Example Trading Ltd",
    "representative_name": "Test Representative",
    "email": "Employer@Example.com",
    "phone": "+8801700000000",
    "country": "Bangladesh",
    "industry": "Recruitment",
    "requested_roles": "Steel Fixer",
    "requirements": "Five workers required",
}


def test_public_submission_saves_request_without_granting_access(monkeypatch):
    import api.employer_access_requests as api

    captured = {}

    def fake_create_request(**kwargs):
        captured.update(kwargs)
        return {
            "id": "request-001",
            "status": "Pending",
            "created_at": "2026-10-12T00:00:00",
        }

    monkeypatch.setattr(
        api._repository, "create_request", fake_create_request
    )

    response = TestClient(app).post("/api/public/employer-access-requests", json=VALID_REQUEST)

    assert response.status_code == 201
    assert response.json()["request"]["status"] == "Pending"
    assert captured["email"] == "employer@example.com"
    assert "user_id" not in captured
    assert "role" not in captured
    assert "organization_id" not in captured


def test_public_submission_rejects_invalid_email():
    payload = {**VALID_REQUEST, "email": "not-an-email"}

    response = TestClient(app).post("/api/public/employer-access-requests", json=payload)

    assert response.status_code == 422


def test_request_list_requires_administrator(monkeypatch):
    import api.employer_access_requests as api

    def deny_access(request):
        raise HTTPException(status_code=403, detail="Forbidden")

    monkeypatch.setattr(api, "require_admin", deny_access)

    response = TestClient(app).get(BASE)

    assert response.status_code == 403


def test_administrator_can_list_pending_requests(monkeypatch):
    import api.employer_access_requests as api

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        api._repository,
        "list_requests",
        lambda **kwargs: [
            {"id": "request-001", "status": "Pending"}
        ],
    )

    response = TestClient(app).get(BASE, params={"status": "Pending"})

    assert response.status_code == 200
    assert response.json()["requests"][0]["status"] == "Pending"


def test_review_records_decision_without_creating_membership(monkeypatch):
    import api.employer_access_requests as api
    import services.local_auth as local_auth

    captured = {}

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        local_auth,
        "get_request_principal",
        lambda request: {
            "id": "admin-001",
            "email": "admin@example.com",
        },
    )

    def fake_review_request(request_id, **kwargs):
        captured["request_id"] = request_id
        captured.update(kwargs)
        return {
            "id": request_id,
            "status": kwargs["status"],
            "reviewed_by": kwargs["reviewed_by"],
            "review_notes": kwargs["review_notes"],
        }

    monkeypatch.setattr(
        api._repository, "review_request", fake_review_request
    )

    response = TestClient(app).patch(
        f"{BASE}/request-001/review",
        json={
            "status": "Approved",
            "review_notes": "Company details reviewed",
        },
    )

    assert response.status_code == 200
    assert response.json()["request"]["status"] == "Approved"
    assert captured["reviewed_by"] == "admin@example.com"
    assert captured["review_notes"] == "Company details reviewed"
    assert "organization_id" not in captured
    assert "role" not in captured


def test_review_requires_administrator_identity(monkeypatch):
    import api.employer_access_requests as api
    import services.local_auth as local_auth

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        local_auth, "get_request_principal", lambda request: None
    )

    response = TestClient(app).patch(
        f"{BASE}/request-001/review",
        json={"status": "Rejected"},
    )

    assert response.status_code == 401


def test_approved_request_sends_employer_email(monkeypatch):
    import api.employer_access_requests as api
    import services.local_auth as local_auth

    captured = {}

    class FakeEmailService:
        def send_email(self, **kwargs):
            captured.update(kwargs)
            return {"status": "Succeeded"}

    record = {
        "id": "request-001",
        "status": "Approved",
        "company_name": "ABC Construction Test Ltd.",
        "representative_name": "Rahim Ahmed",
        "email": "employer@example.com",
    }

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        local_auth,
        "get_request_principal",
        lambda request: {
            "id": "admin-001",
            "email": "admin@example.com",
        },
    )
    monkeypatch.setattr(
        api._repository, "review_request", lambda *args, **kwargs: record
    )
    monkeypatch.setattr(api, "EmailService", FakeEmailService)
    log_events = []

    class FakeDeliveryLogRepository:
        def create_delivery_log(self, **kwargs):
            log_events.append(("create", kwargs))
            return {"id": "delivery-test-001"}

        def update_delivery_status(
            self, delivery_id, status, error_message=None
        ):
            log_events.append(
                ("update", delivery_id, status, error_message)
            )

    monkeypatch.setattr(
        api, "_delivery_log_repository", FakeDeliveryLogRepository()
    )

    response = TestClient(app).patch(
        f"{BASE}/request-001/review",
        json={"status": "Approved"},
    )

    assert response.status_code == 200
    assert response.json()["request"]["status"] == "Approved"
    assert response.json()["notification_status"] == "SENT"
    assert ("update", "delivery-test-001", "SENT", None) in log_events
    assert captured["recipient"] == "employer@example.com"
    assert "ABC Construction Test Ltd." in captured["plain_text"]
    assert "does not create an account" in captured["plain_text"]


def test_rejection_is_preserved_when_email_fails(monkeypatch):
    import api.employer_access_requests as api
    import services.local_auth as local_auth

    class FailingEmailService:
        def send_email(self, **kwargs):
            raise RuntimeError("simulated email failure")

    record = {
        "id": "request-002",
        "status": "Rejected",
        "company_name": "Example Trading Ltd.",
        "representative_name": "Test Representative",
        "email": "employer@example.com",
    }

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        local_auth,
        "get_request_principal",
        lambda request: {
            "id": "admin-001",
            "email": "admin@example.com",
        },
    )
    monkeypatch.setattr(
        api._repository, "review_request", lambda *args, **kwargs: record
    )
    monkeypatch.setattr(api, "EmailService", FailingEmailService)
    log_events = []

    class FakeDeliveryLogRepository:
        def create_delivery_log(self, **kwargs):
            log_events.append(("create", kwargs))
            return {"id": "delivery-test-001"}

        def update_delivery_status(
            self, delivery_id, status, error_message=None
        ):
            log_events.append(
                ("update", delivery_id, status, error_message)
            )

    monkeypatch.setattr(
        api, "_delivery_log_repository", FakeDeliveryLogRepository()
    )

    response = TestClient(app).patch(
        f"{BASE}/request-002/review",
        json={"status": "Rejected"},
    )

    assert response.status_code == 200
    assert response.json()["request"]["status"] == "Rejected"
    assert response.json()["notification_status"] == "FAILED"
    assert any(e[0] == "update" and e[2] == "FAILED" for e in log_events)
    assert "could not be confirmed as sent" in response.json()["message"]

def _prepare_admin_activation_test(monkeypatch, *, status="Approved", fail_email=False):
    from types import SimpleNamespace
    import api.employer_access_requests as api
    import services.local_auth as local_auth

    record = {
        "id": "request-activation-test",
        "status": status,
        "company_name": "Example Construction Ltd",
        "representative_name": "Test Representative",
        "email": "employer@example.com",
    }
    captured = {
        "memberships": [],
        "emails": [],
        "audit": [],
        "delivery": [],
        "profiles": [],
        "mappings": [],
        "existing_members": [],
        "membership_updates": [],
        "mapping_error": False,
        "fail_compensation": False,
        "mapping_after_error": None,
        "mapping_lookup_count": 0,
    }

    monkeypatch.setattr(api, "require_admin", lambda request: {})
    monkeypatch.setattr(
        local_auth,
        "get_request_principal",
        lambda request: {
            "id": "admin-test-id",
            "email": "admin@example.com",
            "name": "Test Administrator",
        },
    )
    monkeypatch.setattr(api._repository, "get_request", lambda request_id: record)

    organization = SimpleNamespace(
        id="org-activation-test",
        name="Example Organization",
        status="active",
    )

    class FakeOrganizationRepository:
        def list_active_organizations(self):
            return [organization]

        def list_members(self, organization_id):
            return list(captured["existing_members"])

        def add_membership(self, *, organization_id, user_id, role):
            captured["memberships"].append({
                "organization_id": organization_id,
                "user_id": user_id,
                "role": role,
            })
            return SimpleNamespace(
                id="membership-test-id",
                organization_id=organization_id,
                user_id=user_id,
                role=role,
                status="active",
            )

        def update_membership_status(self, **kwargs):
            captured["membership_updates"].append(kwargs)
            if kwargs.get("status") == "inactive" and captured["fail_compensation"]:
                raise RuntimeError("simulated membership compensation failure")
            return SimpleNamespace(
                id="membership-test-id",
                organization_id=kwargs["organization_id"],
                user_id=kwargs["user_id"],
                role=kwargs.get("role", "Employer Manager"),
                status=kwargs["status"],
            )

    class FakeUserProfileRepository:
        def __init__(self):
            self.profiles = {}

        def get_profile(self, user_id):
            return self.profiles.get(user_id)

        def get_by_email(self, email):
            matches = [
                profile for profile in self.profiles.values()
                if profile.primary_email.casefold() == email.strip().casefold()
            ]
            if len(matches) > 1:
                raise ValueError("Multiple profiles match this email.")
            return matches[0] if matches else None

        def save_profile(self, profile):
            self.profiles[profile.user_id] = profile
            captured["profiles"].append(profile)
            return profile

    class FakeMappingRepository:
        def __init__(self):
            self.mappings = {}

        def get_mapping(self, *, provider, tenant_id, external_object_id):
            captured["mapping_lookup_count"] += 1
            if (
                captured["mapping_lookup_count"] > 1
                and captured["mapping_after_error"] is not None
            ):
                return captured["mapping_after_error"]
            return self.mappings.get(external_object_id)

        def create_active_mapping(self, **kwargs):
            if captured["mapping_error"]:
                raise RuntimeError("simulated mapping creation failure")
            mapping = {
                "id": "mapping-activation-test",
                **kwargs,
                "status": "Active",
            }
            self.mappings[kwargs["external_object_id"]] = mapping
            captured["mappings"].append(mapping)
            return mapping

    class FakeAuditRepository:
        def create_log(self, **kwargs):
            captured["audit"].append(kwargs)

    class FakeDeliveryLogRepository:
        def create_delivery_log(self, **kwargs):
            captured["delivery"].append(("create", kwargs))
            return {"id": "activation-delivery-test"}

        def update_delivery_status(self, delivery_id, status, error_message=None):
            captured["delivery"].append(
                ("update", delivery_id, status, error_message)
            )

    class FakeEmailService:
        def send_email(self, **kwargs):
            captured["emails"].append(kwargs)
            if fail_email:
                raise RuntimeError("simulated email failure")
            return {"status": "Succeeded"}

    monkeypatch.setattr(
        api.organization_api,
        "_organization_repository",
        FakeOrganizationRepository(),
    )
    monkeypatch.setattr(
        api.organization_api,
        "_audit_log_repository",
        FakeAuditRepository(),
    )
    profile_repository = FakeUserProfileRepository()
    mapping_repository = FakeMappingRepository()
    organization_repository = FakeOrganizationRepository()

    captured["profile_repository"] = profile_repository
    captured["mapping_repository"] = mapping_repository
    captured["organization_repository"] = organization_repository

    monkeypatch.setattr(
        api.organization_api,
        "_organization_repository",
        organization_repository,
    )
    monkeypatch.setattr(api, "_delivery_log_repository", FakeDeliveryLogRepository())
    monkeypatch.setattr(api, "_identity_mapping_repository", mapping_repository)
    monkeypatch.setattr(api, "_user_profile_repository", profile_repository)
    monkeypatch.setattr(api, "EmailService", FakeEmailService)

    return captured


def test_admin_activation_refuses_pending_request(monkeypatch):
    import api.employer_access_requests as api

    captured = _prepare_admin_activation_test(monkeypatch, status="Pending")
    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 409
    assert captured["memberships"] == []
    assert captured["emails"] == []


def test_admin_activation_creates_employer_manager_and_sends_email(monkeypatch):
    captured = _prepare_admin_activation_test(monkeypatch)

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["membership_status"] == "ACTIVE"
    assert body["role"] == "Employer Manager"
    assert body["notification_status"] == "SENT"
    assert captured["memberships"] == [{
        "organization_id": "org-activation-test",
        "user_id": "verified-entra-object-id",
        "role": "Employer Manager",
    }]
    assert len(captured["profiles"]) == 1
    profile = captured["profiles"][0]
    assert profile.user_id == "verified-entra-object-id"
    assert profile.full_name == "Test Representative"
    assert profile.primary_email == "employer@example.com"
    assert len(captured["mappings"]) == 1
    mapping = captured["mappings"][0]
    assert mapping["application_user_id"] == profile.user_id
    assert mapping["external_object_id"] == "verified-entra-object-id"
    assert mapping["verified_by"] == "admin-test-id"
    assert mapping["verification_method"] == "administrator_attestation"
    assert captured["emails"][0]["recipient"] == "employer@example.com"
    assert captured["audit"][0]["action"] == "create"


def test_admin_activation_keeps_membership_when_email_fails(monkeypatch):
    captured = _prepare_admin_activation_test(monkeypatch, fail_email=True)

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["membership_status"] == "ACTIVE"
    assert body["notification_status"] == "FAILED"
    assert len(captured["memberships"]) == 1
    assert captured["memberships"][0]["role"] == "Employer Manager"
    assert (
        "update", "activation-delivery-test", "FAILED",
        "Email send failed (RuntimeError)."
    ) in captured["delivery"]


def test_admin_activation_links_existing_employer_account_without_creating_membership(monkeypatch):
    from types import SimpleNamespace
    import api.employer_access_requests as api

    captured = {"mapping": None, "memberships_added": []}
    _prepare_admin_activation_test(monkeypatch)

    member = SimpleNamespace(
        id="existing-membership-id",
        user_id="canonical-existing-user",
        organization_id="org-activation-test",
        role="Employer Manager",
        status="active",
    )
    monkeypatch.setattr(
        api.organization_api, "_organization_repository",
        type("ExistingMembershipRepository", (), {
            "list_active_organizations": lambda self: [SimpleNamespace(
                id="org-activation-test", name="Example Organization", status="active"
            )],
            "list_members": lambda self, organization_id: [member],
            "add_membership": lambda self, **kwargs: captured["memberships_added"].append(kwargs),
        })(),
    )

    class FakeMappingRepository:
        def get_mapping(self, **kwargs):
            return None
        def create_active_mapping(self, **kwargs):
            captured["mapping"] = kwargs
            return {"id": "mapping-activation-test", **kwargs, "status": "Active"}

    monkeypatch.setattr(api, "_identity_mapping_repository", FakeMappingRepository())

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "new-employer-external-object-id",
            "application_user_id": "canonical-existing-user",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    assert captured["mapping"]["application_user_id"] == "canonical-existing-user"
    assert captured["mapping"]["external_object_id"] == "new-employer-external-object-id"
    assert captured["memberships_added"] == []


def test_admin_activation_reports_audit_failure_without_rolling_back_identity_mapping(monkeypatch):
    from types import SimpleNamespace
    import api.employer_access_requests as api

    captured = _prepare_admin_activation_test(monkeypatch)
    captured["mapping"] = None
    captured["memberships_added"] = []

    member = SimpleNamespace(
        id="existing-membership-id",
        user_id="canonical-existing-user",
        organization_id="org-activation-test",
        role="Employer Manager",
        status="active",
    )

    class ExistingMembershipRepository:
        def list_active_organizations(self):
            return [SimpleNamespace(
                id="org-activation-test",
                name="Example Organization",
                status="active",
            )]

        def list_members(self, organization_id):
            return [member]

        def add_membership(self, **kwargs):
            captured["memberships_added"].append(kwargs)

    monkeypatch.setattr(
        api.organization_api,
        "_organization_repository",
        ExistingMembershipRepository(),
    )

    class FakeMappingRepository:
        def get_mapping(self, **kwargs):
            return None

        def create_active_mapping(self, **kwargs):
            captured["mapping"] = kwargs
            return {
                "id": "mapping-activation-test",
                **kwargs,
                "status": "Active",
            }

    class FailingAuditRepository:
        def create_log(self, **kwargs):
            raise RuntimeError("simulated audit logging failure")

    monkeypatch.setattr(
        api, "_identity_mapping_repository", FakeMappingRepository()
    )
    monkeypatch.setattr(
        api.organization_api, "_audit_log_repository", FailingAuditRepository()
    )

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "new-employer-external-object-id",
            "application_user_id": "canonical-existing-user",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert captured["mapping"]["application_user_id"] == "canonical-existing-user"
    assert captured["mapping"]["external_object_id"] == "new-employer-external-object-id"
    assert captured["memberships_added"] == []
    assert body["audit_status"] == "FAILED"
    assert body["requires_admin_follow_up"] is True
    assert body["audit_warning"]
    assert "audit logging failed" in body["message"].lower()


def test_admin_activation_refuses_link_without_active_employer_manager_membership(monkeypatch):
    import api.employer_access_requests as api
    _prepare_admin_activation_test(monkeypatch)
    captured = []

    class FakeMappingRepository:
        def get_mapping(self, **kwargs):
            return None
        def create_active_mapping(self, **kwargs):
            captured.append(kwargs)
            return {"id": "unexpected"}

    monkeypatch.setattr(api, "_identity_mapping_repository", FakeMappingRepository())
    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "new-employer-external-object-id",
            "application_user_id": "canonical-existing-user",
            "identity_verified": True,
        },
    )
    assert response.status_code == 409
    assert captured == []


def test_admin_activation_reports_delivery_log_update_failure(monkeypatch):
    import api.employer_access_requests as api

    _prepare_admin_activation_test(monkeypatch)

    class FailingDeliveryLogRepository:
        def create_delivery_log(self, **kwargs):
            return {"id": "activation-delivery-test"}

        def update_delivery_status(self, *args, **kwargs):
            raise RuntimeError("simulated delivery log update failure")

    monkeypatch.setattr(
        api,
        "_delivery_log_repository",
        FailingDeliveryLogRepository(),
    )

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["membership_status"] == "ACTIVE"
    assert body["notification_status"] == "SENT"
    assert body["delivery_log_status"] == "FAILED"


def test_admin_activation_reports_delivery_log_creation_failure(monkeypatch):
    import api.employer_access_requests as api

    _prepare_admin_activation_test(monkeypatch)

    class FailingDeliveryLogRepository:
        def create_delivery_log(self, **kwargs):
            raise RuntimeError("simulated delivery log creation failure")

        def update_delivery_status(self, *args, **kwargs):
            raise AssertionError("No delivery log should be updated")

    monkeypatch.setattr(
        api,
        "_delivery_log_repository",
        FailingDeliveryLogRepository(),
    )

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["membership_status"] == "ACTIVE"
    assert body["notification_status"] == "SENT"
    assert body["delivery_log_status"] == "FAILED"


def test_admin_activation_skips_delivery_log_without_recipient(monkeypatch):
    import api.employer_access_requests as api

    captured = _prepare_admin_activation_test(monkeypatch)

    monkeypatch.setattr(
        api._repository,
        "get_request",
        lambda request_id: {
            "id": "request-activation-test",
            "status": "Approved",
            "company_name": "Example Construction Ltd",
            "representative_name": "Test Representative",
            "email": "",
        },
    )

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["membership_status"] == "ACTIVE"
    assert body["delivery_log_status"] == "NOT_ATTEMPTED"
    assert body["delivery_log_warning"] is None
    assert captured["emails"] == []
    assert captured["delivery"] == []


def test_admin_activation_reuses_existing_profile_and_reactivates_membership(monkeypatch):
    from types import SimpleNamespace

    captured = _prepare_admin_activation_test(monkeypatch)
    profile = SimpleNamespace(
        user_id="verified-entra-object-id",
        full_name="Existing Representative",
        primary_email="employer@example.com",
        phone="+8801700000000",
    )
    captured["profile_repository"].profiles[profile.user_id] = profile

    captured["existing_members"].append(SimpleNamespace(
        id="inactive-membership-id",
        organization_id="org-activation-test",
        user_id=profile.user_id,
        role="Employer Manager",
        status="inactive",
    ))

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    assert captured["profiles"] == []
    assert captured["memberships"] == []
    assert captured["membership_updates"] == [{
        "organization_id": "org-activation-test",
        "user_id": profile.user_id,
        "status": "active",
        "role": "Employer Manager",
    }]
    assert len(captured["mappings"]) == 1
    assert captured["mappings"][0]["application_user_id"] == profile.user_id


def test_admin_activation_refuses_existing_active_membership(monkeypatch):
    from types import SimpleNamespace

    captured = _prepare_admin_activation_test(monkeypatch)
    profile = SimpleNamespace(
        user_id="verified-entra-object-id",
        full_name="Existing Representative",
        primary_email="employer@example.com",
        phone="",
    )
    captured["profile_repository"].profiles[profile.user_id] = profile
    captured["existing_members"].append(SimpleNamespace(
        id="active-membership-id",
        organization_id="org-activation-test",
        user_id=profile.user_id,
        role="Employer Manager",
        status="active",
    ))

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 409, response.text
    assert captured["membership_updates"] == []
    assert captured["mappings"] == []


def test_admin_activation_refuses_inactive_membership_with_different_role(monkeypatch):
    from types import SimpleNamespace

    captured = _prepare_admin_activation_test(monkeypatch)
    profile = SimpleNamespace(
        user_id="verified-entra-object-id",
        full_name="Existing Representative",
        primary_email="employer@example.com",
        phone="",
    )
    captured["profile_repository"].profiles[profile.user_id] = profile
    captured["existing_members"].append(SimpleNamespace(
        id="inactive-membership-id",
        organization_id="org-activation-test",
        user_id=profile.user_id,
        role="Candidate",
        status="inactive",
    ))

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 409, response.text
    assert captured["membership_updates"] == []
    assert captured["mappings"] == []


def test_admin_activation_compensates_when_mapping_creation_fails(monkeypatch):
    captured = _prepare_admin_activation_test(monkeypatch)
    captured["mapping_error"] = True

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 503, response.text
    assert "membership was deactivated" in response.json()["detail"].lower()
    assert len(captured["memberships"]) == 1
    assert captured["membership_updates"] == [{
        "organization_id": "org-activation-test",
        "user_id": "verified-entra-object-id",
        "status": "inactive",
        "role": "Employer Manager",
    }]
    assert captured["mappings"] == []


def test_admin_activation_reports_mapping_and_compensation_failure(monkeypatch):
    captured = _prepare_admin_activation_test(monkeypatch)
    captured["mapping_error"] = True
    captured["fail_compensation"] = True

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 503, response.text
    assert "compensation also failed" in response.json()["detail"].lower()
    assert len(captured["memberships"]) == 1
    assert len(captured["membership_updates"]) == 1
    assert captured["membership_updates"][0]["status"] == "inactive"
    assert captured["mappings"] == []


def test_admin_activation_accepts_mapping_committed_for_same_user(monkeypatch):
    captured = _prepare_admin_activation_test(monkeypatch)
    captured["mapping_error"] = True
    captured["mapping_after_error"] = {
        "id": "mapping-committed-before-error",
        "application_user_id": "verified-entra-object-id",
        "status": "Active",
    }

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 200, response.text
    assert len(captured["memberships"]) == 1
    assert captured["membership_updates"] == []
    assert captured["mappings"] == []


def test_admin_activation_compensates_when_mapping_belongs_to_another_user(
    monkeypatch,
):
    captured = _prepare_admin_activation_test(monkeypatch)
    captured["mapping_error"] = True
    captured["mapping_after_error"] = {
        "id": "mapping-owned-by-another-user",
        "application_user_id": "different-application-user",
        "status": "Active",
    }

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 409, response.text
    assert "membership was deactivated" in response.json()["detail"].lower()
    assert len(captured["memberships"]) == 1
    assert len(captured["membership_updates"]) == 1
    assert captured["membership_updates"][0]["status"] == "inactive"
    assert captured["mapping_after_error"]["application_user_id"] == (
        "different-application-user"
    )


def test_admin_activation_reports_conflict_when_compensation_fails(monkeypatch):
    captured = _prepare_admin_activation_test(monkeypatch)
    captured["mapping_error"] = True
    captured["fail_compensation"] = True
    captured["mapping_after_error"] = {
        "id": "mapping-owned-by-another-user",
        "application_user_id": "different-application-user",
        "status": "Active",
    }

    response = TestClient(app).post(
        f"{BASE}/request-activation-test/activate",
        json={
            "organization_id": "org-activation-test",
            "entra_object_id": "verified-entra-object-id",
            "identity_verified": True,
        },
    )

    assert response.status_code == 503, response.text
    assert "compensation also failed" in response.json()["detail"].lower()
    assert len(captured["membership_updates"]) == 1
    assert captured["membership_updates"][0]["status"] == "inactive"
