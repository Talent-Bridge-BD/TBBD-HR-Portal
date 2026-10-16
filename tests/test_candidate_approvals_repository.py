import pytest

from repositories.candidate_approvals import (
    InMemoryCandidateApprovalRepository,
)


@pytest.fixture
def repository():
    return InMemoryCandidateApprovalRepository()


def test_new_candidate_starts_pending(repository):
    record = repository.ensure_candidate("candidate-001")

    assert record["approval_status"] == "pending"
    assert record["reviewed_by"] is None
    assert record["reviewed_at"] is None


def test_ensure_candidate_preserves_existing_decision(repository):
    repository.ensure_candidate("candidate-001")

    repository.review_candidate(
        "candidate-001",
        status="approved",
        reviewed_by="admin-test",
    )

    record = repository.ensure_candidate("candidate-001")

    assert record["approval_status"] == "approved"
    assert record["reviewed_by"] == "admin-test"


def test_second_review_cannot_overwrite_decision(repository):
    repository.ensure_candidate("candidate-001")

    repository.review_candidate(
        "candidate-001",
        status="approved",
        reviewed_by="admin-test",
    )

    result = repository.review_candidate(
        "candidate-001",
        status="rejected",
        reviewed_by="another-admin",
    )

    assert result is None
    assert (
        repository.get_approval("candidate-001")["approval_status"]
        == "approved"
    )


def test_list_approvals_filters_by_status(repository):
    repository.ensure_candidate("candidate-001")
    repository.ensure_candidate("candidate-002")

    repository.review_candidate(
        "candidate-002",
        status="approved",
        reviewed_by="admin-test",
    )

    assert len(repository.list_approvals(status="pending")) == 1
    assert len(repository.list_approvals(status="approved")) == 1
    assert repository.list_approvals(status="rejected") == []


def test_invalid_review_status_is_rejected(repository):
    repository.ensure_candidate("candidate-001")

    with pytest.raises(ValueError):
        repository.review_candidate(
            "candidate-001",
            status="pending",
            reviewed_by="admin-test",
        )


def test_missing_candidate_cannot_be_reviewed(repository):
    result = repository.review_candidate(
        "candidate-missing",
        status="approved",
        reviewed_by="admin-test",
    )

    assert result is None
