from types import SimpleNamespace

from services.authorization import build_authorization_context


def test_employer_manager_role_aliases_collapse_to_one_canonical_role():
    user_id = "11b262fd-ca4c-4b7a-9035-69261eb72cc9"
    organization_id = "005f50d3-26ab-f111-9b32-000d3ac9134a"

    membership = SimpleNamespace(
        user_id=user_id,
        organization_id=organization_id,
        role="Employer Manager",
        status="active",
    )

    context = build_authorization_context(
        user_id=user_id,
        roles={"Employer.Manager", "Employer Manager"},
        memberships=[membership],
    )

    assert context.roles == frozenset({"Employer Manager"})
    assert context.organization_ids == frozenset({organization_id})
    assert not context.is_global_administrator


def test_role_normalization_preserves_other_roles():
    context = build_authorization_context(
        user_id="test-user",
        roles={"Administrator", "Candidate", "HR Manager"},
        memberships=[],
    )

    assert context.roles == frozenset({
        "Administrator",
        "Candidate",
        "HR Manager",
    })
    assert context.is_global_administrator
