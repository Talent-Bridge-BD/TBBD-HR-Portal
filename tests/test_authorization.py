import base64
import json

def make_principal(principal_id, name, groups=None, roles=None):
    principal = {
        "claims": [
            {"typ": "name", "val": name},
            *[
                {"typ": "groups", "val": group}
                for group in (groups or [])
            ],
            *[
                {"typ": "roles", "val": role}
                for role in (roles or [])
            ],
        ]
    }
    return base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")


from repositories.organization import InMemoryOrganizationRepository
from models.organization import OrganizationMembership
from services.authorization_service import AuthorizationService


def test_authorization_context_contains_only_active_user_memberships():
    repository = InMemoryOrganizationRepository()

    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id="org-001",
            user_id="user-001",
            role="Employer Manager",
            status="active",
        ),
        OrganizationMembership(
            id="membership-002",
            organization_id="org-002",
            user_id="user-001",
            role="Employer Manager",
            status="revoked",
        ),
        OrganizationMembership(
            id="membership-003",
            organization_id="org-003",
            user_id="user-002",
            role="Employer Manager",
            status="active",
        ),
    ]

    service = AuthorizationService(repository)

    context = service.build_context(
        user_id="user-001",
        roles={"Employer Manager"},
    )

    assert context.user_id == "user-001"
    assert context.roles == frozenset({"Employer Manager"})
    assert context.organization_ids == frozenset({"org-001"})


def test_organization_repository_lists_only_active_organizations():

    from models.organization import Organization

    repository = InMemoryOrganizationRepository()

    repository._organizations = [
        Organization(
            id="org-001",
            name="Active Employer",
            status="active",
        ),
        Organization(
            id="org-002",
            name="Inactive Employer",
            status="inactive",
        ),
    ]

    organizations = repository.list_active_organizations()

    assert organizations == [
        Organization(
            id="org-001",
            name="Active Employer",
            status="active",
        )
    ]


def test_administrator_has_global_scope_without_organization_membership():

    repository = InMemoryOrganizationRepository()

    service = AuthorizationService(repository)

    context = service.build_context(
        user_id="admin-001",
        roles={"Administrator"},
    )

    assert context.roles == frozenset({"Administrator"})
    assert context.organization_ids == frozenset()
    assert context.is_global_administrator is True


def test_employer_manager_is_not_global_administrator():

    repository = InMemoryOrganizationRepository()

    repository._memberships = [
        OrganizationMembership(
            id="membership-001",
            organization_id="org-001",
            user_id="employer-001",
            role="Employer Manager",
            status="active",
        ),
    ]

    service = AuthorizationService(repository)

    context = service.build_context(
        user_id="employer-001",
        roles={"Employer Manager"},
    )

    assert context.organization_ids == frozenset({"org-001"})
    assert context.is_global_administrator is False


def test_job_repository_lists_jobs_for_global_administrator_scope():
    from models.job import Job
    from repositories.job import InMemoryJobRepository

    repository = InMemoryJobRepository()
    repository._jobs = {
        "job-001": Job(
            id="job-001",
            organization_id="org-001",
            title="Office Executive",
        ),
        "job-002": Job(
            id="job-002",
            organization_id="org-002",
            title="Software Engineer",
        ),
    }

    jobs = repository.list_all_active_organization_jobs()

    assert {job.id for job in jobs} == {"job-001", "job-002"}


def test_administrator_can_list_jobs_for_selected_organization(monkeypatch):
    import api.job as job_api
    from fastapi.testclient import TestClient
    from main import app
    from models.job import Job

    jobs_by_organization = {
        "org-001": [
            Job(
                id="job-001",
                organization_id="org-001",
                title="Office Executive",
            ),
        ],
        "org-002": [
            Job(
                id="job-002",
                organization_id="org-002",
                title="Software Engineer",
            ),
        ],
    }

    monkeypatch.setattr(
        job_api,
        "_job_service",
        type(
            "FakeJobService",
            (),
            {
                "list_jobs": (
                    lambda self, organization_id:
                    jobs_by_organization[organization_id]
                ),
            },
        )(),
    )

    monkeypatch.setattr(
        job_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: []
                ),
            },
        )(),
    )

    principal = make_principal(
        "admin-001",
        "Test Administrator",
        roles=["Administrator"],
    )

    client = TestClient(app)
    response = client.get(
        "/api/jobs?organization_id=org-001",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "admin-001",
            "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.com",
            "X-MS-CLIENT-PRINCIPAL": principal,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert {job["id"] for job in data["jobs"]} == {"job-001"}
    assert all(
        job["organization_id"] == "org-001"
        for job in data["jobs"]
    )


def test_employer_manager_cannot_list_jobs_for_another_organization(
    monkeypatch,
):
    import api.job as job_api
    from fastapi.testclient import TestClient
    from main import app
    from models.organization import OrganizationMembership

    monkeypatch.setattr(
        job_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: [
                        OrganizationMembership(
                            id="membership-001",
                            organization_id="org-001",
                            user_id=user_id,
                            role="Employer Manager",
                            status="active",
                        )
                    ]
                ),
            },
        )(),
    )

    principal = make_principal(
        "employer-001",
        "Test Employer",
        roles=["Employer Manager"],
    )

    client = TestClient(app)
    response = client.get(
        "/api/jobs?organization_id=org-002",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "employer-001",
            "X-MS-CLIENT-PRINCIPAL-NAME": "employer@example.com",
            "X-MS-CLIENT-PRINCIPAL": principal,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "User is not authorized for this organization"
    )
