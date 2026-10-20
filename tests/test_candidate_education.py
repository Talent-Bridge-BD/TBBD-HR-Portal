from datetime import date, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from api.candidate import CandidateEducationRequest
from repositories.candidate_education import SqlCandidateEducationRepository


def make_row(**overrides):
    values = {
        "id": "education-001",
        "candidate_id": "candidate-db-001",
        "degree_qualification": "",
        "institution": "",
        "field_of_study": None,
        "start_date": None,
        "end_date": None,
        "description": None,
        "created_at": datetime(2026, 1, 1),
        "updated_at": datetime(2026, 1, 1),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class FakeCursor:
    def __init__(self, rows=None, rowcount=1):
        self.rows = list(rows or [])
        self.rowcount = rowcount
        self.calls = []
        self.last_row = None

    def execute(self, sql, *params):
        self.calls.append((sql, params))
        normalized = " ".join(sql.split()).upper()

        if normalized.startswith("INSERT INTO DBO.CANDIDATE_EDUCATION"):
            self.last_row = self.rows.pop(0) if self.rows else None
        elif normalized.startswith("SELECT"):
            self.last_row = self.rows.pop(0) if self.rows else None

        return self

    def fetchone(self):
        return self.last_row

    def fetchall(self):
        rows = []
        if self.last_row is not None:
            rows.append(self.last_row)
        rows.extend(self.rows)
        self.rows = []
        return rows


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def make_repository(monkeypatch, *connections):
    repository = SqlCandidateEducationRepository.__new__(
        SqlCandidateEducationRepository
    )
    connection_iter = iter(connections)
    monkeypatch.setattr(
        repository,
        "_connection",
        lambda: next(connection_iter),
    )
    return repository


def test_education_request_allows_every_field_to_be_omitted():
    payload = CandidateEducationRequest()

    assert payload.degree_qualification is None
    assert payload.institution is None
    assert payload.field_of_study is None
    assert payload.start_date is None
    assert payload.end_date is None
    assert payload.description is None


def test_education_request_normalizes_blank_optional_text():
    payload = CandidateEducationRequest(
        degree_qualification="  ",
        institution="  ",
        field_of_study=" Computer Science ",
        description="  ",
    )

    assert payload.degree_qualification is None
    assert payload.institution is None
    assert payload.field_of_study == "Computer Science"
    assert payload.description is None


def test_education_request_accepts_optional_iso_dates():
    payload = CandidateEducationRequest(
        start_date="2020-01-01",
        end_date="2024-12-31",
    )
    payload.validate_date_range()

    assert payload.start_date == "2020-01-01"
    assert payload.end_date == "2024-12-31"


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [
        ("2024-01-01", "2020-01-01"),
        ("not-a-date", None),
        (None, "2026-02-30"),
    ],
)
def test_education_request_rejects_invalid_dates_or_ranges(
    start_date, end_date
):
    if start_date == "2024-01-01":
        payload = CandidateEducationRequest(
            start_date=start_date,
            end_date=end_date,
        )
        with pytest.raises(ValueError, match="End date cannot be before"):
            payload.validate_date_range()
    else:
        with pytest.raises(ValidationError):
            CandidateEducationRequest(
                start_date=start_date,
                end_date=end_date,
            )


def test_row_mapping_displays_required_text_columns_as_blank_when_empty():
    education = SqlCandidateEducationRepository._map_row(make_row())

    assert education.degree_qualification == ""
    assert education.institution == ""
    assert education.field_of_study is None
    assert education.start_date is None
    assert education.end_date is None


def test_list_education_scopes_query_to_candidate_identity(monkeypatch):
    cursor = FakeCursor(rows=[make_row()])
    connection = FakeConnection(cursor)
    repository = make_repository(monkeypatch, connection)

    result = repository.list_education("entra-candidate-001")

    sql, params = cursor.calls[0]
    assert "INNER JOIN dbo.candidates AS c ON c.id = e.candidate_id" in sql
    assert "WHERE c.entra_object_id = ?" in sql
    assert params == ("entra-candidate-001",)
    assert len(result) == 1
    assert result[0].id == "education-001"


def test_create_education_allows_empty_fields_and_scopes_candidate(
    monkeypatch,
):
    cursor = FakeCursor(rows=[make_row()])
    connection = FakeConnection(cursor)
    repository = make_repository(monkeypatch, connection)

    saved = repository.create_education(
        "entra-candidate-001",
        None,
        None,
        None,
        None,
        None,
        None,
    )

    sql, params = cursor.calls[0]
    assert "INSERT INTO dbo.candidate_education" in sql
    assert "WHERE c.entra_object_id = ?" in sql
    assert params == (
        "",
        "",
        None,
        None,
        None,
        None,
        "entra-candidate-001",
    )
    assert connection.committed
    assert saved.degree_qualification == ""
    assert saved.institution == ""


def test_create_education_rolls_back_if_candidate_is_not_found(monkeypatch):
    cursor = FakeCursor(rows=[])
    connection = FakeConnection(cursor)
    repository = make_repository(monkeypatch, connection)

    with pytest.raises(ValueError, match="Candidate profile not found"):
        repository.create_education(
            "missing-candidate",
            None,
            None,
            None,
            None,
            None,
            None,
        )

    assert connection.rolled_back
    assert not connection.committed


def test_update_education_scopes_record_to_candidate(monkeypatch):
    cursor = FakeCursor(rowcount=0)
    connection = FakeConnection(cursor)
    repository = make_repository(monkeypatch, connection)

    result = repository.update_education(
        "entra-candidate-001",
        "education-001",
        None,
        None,
        None,
        None,
        None,
        None,
    )

    sql, params = cursor.calls[0]
    assert "WHERE e.id = ? AND c.entra_object_id = ?" in sql
    assert params[-2:] == (
        "education-001",
        "entra-candidate-001",
    )
    assert result is None
    assert connection.rolled_back
    assert not connection.committed


def test_delete_education_scopes_record_to_candidate(monkeypatch):
    cursor = FakeCursor(rowcount=0)
    connection = FakeConnection(cursor)
    repository = make_repository(monkeypatch, connection)

    deleted = repository.delete_education(
        "entra-candidate-001",
        "education-owned-by-someone-else",
    )

    sql, params = cursor.calls[0]
    assert "WHERE e.id = ? AND c.entra_object_id = ?" in sql
    assert params == (
        "education-owned-by-someone-else",
        "entra-candidate-001",
    )
    assert not deleted
    assert connection.rolled_back
    assert not connection.committed
