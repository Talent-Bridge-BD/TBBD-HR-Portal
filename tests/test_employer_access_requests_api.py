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
    captured = {"memberships": [], "emails": [], "audit": [], "delivery": []}

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
            return []

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
            raise AssertionError("No inactive membership was expected in this test")

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
        api.organization_api, "_organization_repository",
        FakeOrganizationRepository(),
    )
    monkeypatch.setattr(
        api.organization_api, "_audit_log_repository",
        FakeAuditRepository(),
    )
    monkeypatch.setattr(api, "_delivery_log_repository", FakeDeliveryLogRepository())
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
