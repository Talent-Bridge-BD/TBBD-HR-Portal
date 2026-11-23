import base64
import json

from fastapi.testclient import TestClient

from main import app
from models.organization import Organization
from repositories.employer_access_requests import (
    EmployerOrganizationConflictError,
    InMemoryEmployerAccessRequestRepository,
)


ADMIN_ID = "admin-001"
EMPLOYER_ID = "employer-001"


def make_principal(principal_id, name, roles=None):
    principal = {
        "claims": [
            {"typ": "name", "val": name},
            *[
                {"typ": "roles", "val": role}
                for role in (roles or [])
            ],
        ]
    }
    return base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")


def admin_headers():
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": ADMIN_ID,
        "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.com",
        "X-MS-CLIENT-PRINCIPAL": make_principal(
            ADMIN_ID,
            "Test Administrator",
            roles=["Administrator"],
        ),
    }


def employer_headers():
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": EMPLOYER_ID,
        "X-MS-CLIENT-PRINCIPAL-NAME": "employer@example.com",
        "X-MS-CLIENT-PRINCIPAL": make_principal(
            EMPLOYER_ID,
            "Test Employer",
            roles=["Employer Manager"],
        ),
    }


def make_request(repository, company_name="Example Employer Ltd"):
    return repository.create_request({
        "company_name": company_name,
        "representative_name": "Test Representative",
        "email": "representative@example.com",
        "phone": "+8801700000000",
        "country": "Bangladesh",
        "industry": "Technology",
        "requested_roles": "Employer Manager",
        "requirements": "Test onboarding request",
    })


def test_approved_request_creates_and_links_organization():
    repository = InMemoryEmployerAccessRequestRepository()
    request_item = make_request(repository)

    reviewed = repository.review_request(
        request_item["id"],
        status="approved",
        reviewed_by=ADMIN_ID,
    )

    assert reviewed is not None
    assert reviewed["status"] == "approved"
    assert reviewed["organization_id"]

    assert len(repository._organizations) == 1
    organization = repository._organizations[0]

    assert organization.id == reviewed["organization_id"]
    assert organization.name == request_item["company_name"]
    assert organization.status == "active"


def test_rejected_request_does_not_create_organization():
    repository = InMemoryEmployerAccessRequestRepository()
    request_item = make_request(repository)

    reviewed = repository.review_request(
        request_item["id"],
        status="rejected",
        reviewed_by=ADMIN_ID,
    )

    assert reviewed is not None
    assert reviewed["status"] == "rejected"
    assert reviewed["organization_id"] is None
    assert repository._organizations == []


def test_duplicate_organization_name_is_rejected_case_insensitively():
    repository = InMemoryEmployerAccessRequestRepository()
    request_item = make_request(
        repository,
        company_name="Example Employer Ltd",
    )

    repository._organizations.append(
        Organization(
            id="existing-org-001",
            name="EXAMPLE EMPLOYER LTD",
            status="active",
        )
    )

    try:
        repository.review_request(
            request_item["id"],
            status="approved",
            reviewed_by=ADMIN_ID,
        )
        assert False, "Expected an organization conflict"
    except EmployerOrganizationConflictError:
        pass

    assert repository._requests[0]["status"] == "pending"
    assert repository._requests[0]["organization_id"] is None
    assert len(repository._organizations) == 1


def test_already_reviewed_request_cannot_be_reviewed_again():
    repository = InMemoryEmployerAccessRequestRepository()
    request_item = make_request(repository)

    first_review = repository.review_request(
        request_item["id"],
        status="approved",
        reviewed_by=ADMIN_ID,
    )

    second_review = repository.review_request(
        request_item["id"],
        status="rejected",
        reviewed_by=ADMIN_ID,
    )

    assert first_review is not None
    assert second_review is None
    assert len(repository._organizations) == 1
    assert repository._requests[0]["status"] == "approved"


def test_administrator_can_approve_request_and_create_organization(
    monkeypatch,
):
    import api.employer_access_requests as employer_api

    repository = InMemoryEmployerAccessRequestRepository()
    request_item = make_request(repository)

    monkeypatch.setattr(
        employer_api,
        "_repository",
        repository,
    )

    response = TestClient(app).post(
        (
            "/api/administrator/employer-access-requests/"
            f"{request_item['id']}/review"
        ),
        headers=admin_headers(),
        json={"status": "approved"},
    )

    assert response.status_code == 200

    reviewed = response.json()["item"]
    assert reviewed["status"] == "approved"
    assert reviewed["organization_id"]

    assert len(repository._organizations) == 1
    assert (
        repository._organizations[0].id
        == reviewed["organization_id"]
    )


def test_api_returns_conflict_for_existing_organization_name(
    monkeypatch,
):
    import api.employer_access_requests as employer_api

    repository = InMemoryEmployerAccessRequestRepository()
    request_item = make_request(repository)

    repository._organizations.append(
        Organization(
            id="existing-org-002",
            name=request_item["company_name"],
            status="active",
        )
    )

    monkeypatch.setattr(
        employer_api,
        "_repository",
        repository,
    )

    response = TestClient(app).post(
        (
            "/api/administrator/employer-access-requests/"
            f"{request_item['id']}/review"
        ),
        headers=admin_headers(),
        json={"status": "approved"},
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "An organization with this company name already exists"
    )

    assert repository._requests[0]["status"] == "pending"


def test_non_administrator_cannot_review_employer_request(
    monkeypatch,
):
    import api.employer_access_requests as employer_api

    repository = InMemoryEmployerAccessRequestRepository()
    request_item = make_request(repository)

    monkeypatch.setattr(
        employer_api,
        "_repository",
        repository,
    )

    response = TestClient(app).post(
        (
            "/api/administrator/employer-access-requests/"
            f"{request_item['id']}/review"
        ),
        headers=employer_headers(),
        json={"status": "approved"},
    )

    assert response.status_code == 403
    assert repository._requests[0]["status"] == "pending"
    assert repository._organizations == []


# Mocked SQL transaction tests: these never connect to Azure SQL.
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pyodbc

from repositories.employer_access_requests import (
    SqlEmployerAccessRequestRepository,
)


class FakeSqlCursor:
    def __init__(self, fetch_results, insert_error=None):
        self.fetch_results = list(fetch_results)
        self.insert_error = insert_error
        self.statements = []

    def execute(self, query, *parameters):
        self.statements.append((query, parameters))

        if (
            "INSERT INTO dbo.organizations" in query
            and self.insert_error is not None
        ):
            raise self.insert_error

        return self

    def fetchone(self):
        if not self.fetch_results:
            return None
        return self.fetch_results.pop(0)


class FakeSqlConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = 0
        self.rollbacks = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def make_sql_result_row(status, organization_id):
    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        id=uuid4(),
        company_name="Example Employer Ltd",
        representative_name="Test Representative",
        email="representative@example.com",
        phone=None,
        country="Bangladesh",
        industry="Technology",
        requested_roles="Employer Manager",
        requirements=None,
        status=status,
        reviewed_by=ADMIN_ID,
        reviewed_at=now,
        review_notes=None,
        created_at=now,
        updated_at=now,
        organization_id=organization_id,
    )


def make_sql_repository(monkeypatch, cursor):
    connection = FakeSqlConnection(cursor)
    repository = SqlEmployerAccessRequestRepository()
    monkeypatch.setattr(
        repository,
        "_connection",
        lambda: connection,
    )
    return repository, connection


def test_sql_approval_creates_organization_and_commits_atomically(
    monkeypatch,
):
    request_id = str(uuid4())
    organization_id = str(uuid4())

    cursor = FakeSqlCursor([
        SimpleNamespace(company_name="Example Employer Ltd"),
        make_sql_result_row("approved", organization_id),
    ])
    repository, connection = make_sql_repository(monkeypatch, cursor)

    result = repository.review_request(
        request_id,
        status="approved",
        reviewed_by=ADMIN_ID,
    )

    assert result["status"] == "approved"
    assert result["organization_id"] == organization_id
    assert connection.commits == 1
    assert connection.rollbacks == 0

    statements = [query for query, _ in cursor.statements]
    assert any(
        "INSERT INTO dbo.organizations" in query
        for query in statements
    )
    assert any(
        "UPDATE dbo.employer_access_requests" in query
        for query in statements
    )


def test_sql_duplicate_organization_rolls_back_approval(monkeypatch):
    request_id = str(uuid4())

    cursor = FakeSqlCursor(
        [SimpleNamespace(company_name="Example Employer Ltd")],
        insert_error=pyodbc.IntegrityError("duplicate organization"),
    )
    repository, connection = make_sql_repository(monkeypatch, cursor)

    try:
        repository.review_request(
            request_id,
            status="approved",
            reviewed_by=ADMIN_ID,
        )
        assert False, "Expected an organization conflict"
    except EmployerOrganizationConflictError:
        pass

    assert connection.commits == 0
    assert connection.rollbacks == 1

    statements = [query for query, _ in cursor.statements]
    assert any(
        "INSERT INTO dbo.organizations" in query
        for query in statements
    )
    assert not any(
        "UPDATE dbo.employer_access_requests" in query
        for query in statements
    )


def test_sql_rejection_does_not_insert_organization(monkeypatch):
    request_id = str(uuid4())

    cursor = FakeSqlCursor([
        SimpleNamespace(company_name="Example Employer Ltd"),
        make_sql_result_row("rejected", None),
    ])
    repository, connection = make_sql_repository(monkeypatch, cursor)

    result = repository.review_request(
        request_id,
        status="rejected",
        reviewed_by=ADMIN_ID,
    )

    assert result["status"] == "rejected"
    assert result["organization_id"] is None
    assert connection.commits == 1
    assert connection.rollbacks == 0

    statements = [query for query, _ in cursor.statements]
    assert not any(
        "INSERT INTO dbo.organizations" in query
        for query in statements
    )
    assert any(
        "UPDATE dbo.employer_access_requests" in query
        for query in statements
    )


def test_sql_missing_pending_request_rolls_back_without_creating_org(
    monkeypatch,
):
    request_id = str(uuid4())

    cursor = FakeSqlCursor([None])
    repository, connection = make_sql_repository(monkeypatch, cursor)

    result = repository.review_request(
        request_id,
        status="approved",
        reviewed_by=ADMIN_ID,
    )

    assert result is None
    assert connection.commits == 0
    assert connection.rollbacks == 1

    statements = [query for query, _ in cursor.statements]
    assert not any(
        "INSERT INTO dbo.organizations" in query
        for query in statements
    )
    assert not any(
        "UPDATE dbo.employer_access_requests" in query
        for query in statements
    )
