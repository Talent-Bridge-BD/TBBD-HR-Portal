from datetime import date
from types import SimpleNamespace

import pytest

from models.candidate import CandidateProfile
from repositories.candidate import SqlCandidateRepository


def make_row(**overrides):
    values = {
        "id": "candidate-db-id",
        "entra_object_id": "candidate-123",
        "first_name": "Test",
        "last_name": "Candidate",
        "email": "candidate@example.test",
        "phone": "01700000000",
        "date_of_birth": date(1995, 4, 12),
        "address": "House 10, Dhaka",
        "gender": "Male",
        "nationality": "Bangladeshi",
        "nid_number": "NID-123",
        "city": "Dhaka",
        "country": "Bangladesh",
        "professional_summary": "Experienced worker",
        "current_title": "Engineer",
        "career_level": "Mid",
        "years_experience": 5,
        "passport_number": "P123456",
        "passport_country": "Bangladesh",
        "passport_issue_date": date(2022, 1, 15),
        "passport_expiry_date": date(2032, 1, 14),
        "passport_status": "Valid",
        "international_travel_readiness": "Ready",
        "workflow_status": "Applied",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class FakeCursor:
    def __init__(self, existing=None, output_row=None):
        self.existing = existing
        self.output_row = output_row or make_row()
        self.last_row = None
        self.calls = []

    def execute(self, sql, *params):
        self.calls.append((sql, params))
        normalized = " ".join(sql.split()).upper()

        if normalized.startswith("SELECT ID FROM DBO.CANDIDATES"):
            self.last_row = self.existing
        elif normalized.startswith("INSERT INTO DBO.CANDIDATES"):
            self.last_row = self.output_row
        elif normalized.startswith("UPDATE DBO.CANDIDATES"):
            self.last_row = self.output_row
        else:
            self.last_row = None
        return self

    def fetchone(self):
        return self.last_row


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True


def make_repository(monkeypatch, cursor):
    repository = SqlCandidateRepository.__new__(SqlCandidateRepository)
    connection = FakeConnection(cursor)
    monkeypatch.setattr(repository, "_connection", lambda: connection)
    return repository, connection


def test_sql_row_mapping_includes_personal_and_passport_fields():
    profile = SqlCandidateRepository._row_to_profile(
        make_row(),
        resume_document_id="resume-123",
    )

    assert profile.date_of_birth == "1995-04-12"
    assert profile.gender == "Male"
    assert profile.nationality == "Bangladeshi"
    assert profile.nid_number == "NID-123"
    assert profile.full_address == "House 10, Dhaka"
    assert profile.location == "Dhaka, Bangladesh"
    assert profile.passport_issue_date == "2022-01-15"
    assert profile.passport_expiry_date == "2032-01-14"
    assert profile.resume_document_id == "resume-123"
    assert profile.workflow_status == "Applied"


def test_sql_row_mapping_handles_null_personal_fields():
    row = make_row(
        date_of_birth=None,
        address=None,
        gender=None,
        nationality=None,
        nid_number=None,
        passport_issue_date=None,
        passport_expiry_date=None,
    )

    profile = SqlCandidateRepository._row_to_profile(row)

    assert profile.date_of_birth is None
    assert profile.full_address == ""
    assert profile.gender == ""
    assert profile.nationality == "Bangladeshi"
    assert profile.nid_number == ""
    assert profile.passport_issue_date is None
    assert profile.passport_expiry_date is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1995-04-12", date(1995, 4, 12)),
        (date(1995, 4, 12), date(1995, 4, 12)),
        (None, None),
        ("", None),
    ],
)
def test_sql_date_conversion(value, expected):
    assert SqlCandidateRepository._sql_date(value) == expected


def test_save_new_profile_uses_only_existing_database_columns(monkeypatch):
    cursor = FakeCursor(existing=None, output_row=make_row())
    repository, connection = make_repository(monkeypatch, cursor)
    profile = CandidateProfile(
        user_id="candidate-123",
        first_name="Test",
        last_name="",
        email="candidate@example.test",
        phone="01700000000",
        location="Dhaka, Bangladesh",
        date_of_birth="1995-04-12",
        full_address="House 10, Dhaka",
        passport_expiry_date="2032-01-14",
        gender="Male",
        nationality="Bangladeshi",
        nid_number="NID-123",
        passport_issue_date="2022-01-15",
    )

    saved = repository.save_profile(profile)
    insert_sql, params = next(
        (sql, params) for sql, params in cursor.calls
        if "INSERT INTO dbo.candidates" in sql
    )

    for field in ("gender", "nationality", "nid_number", "passport_issue_date"):
        assert field in insert_sql.lower()
    assert len(params) == 24
    assert params[2] == ""
    assert params[5] == date(1995, 4, 12)
    assert params[6] == "House 10, Dhaka"
    assert params[7] == "Dhaka"
    assert params[8] == "Bangladesh"
    assert params[15] == "Male"
    assert params[16] == "Bangladeshi"
    assert params[17] == "NID-123"
    assert params[18] == date(2022, 1, 15)
    assert params[19] == date(2032, 1, 14)
    assert params[-1] == "incomplete"
    assert connection.committed
    assert saved.gender == "Male"
    assert saved.nationality == "Bangladeshi"
    assert saved.nid_number == "NID-123"
    assert saved.passport_issue_date == "2022-01-15"


def test_save_existing_profile_updates_only_existing_database_columns(monkeypatch):
    cursor = FakeCursor(
        existing=SimpleNamespace(id="existing-candidate-id"),
        output_row=make_row(),
    )
    repository, connection = make_repository(monkeypatch, cursor)
    profile = CandidateProfile(
        user_id="candidate-123",
        first_name="Test",
        last_name="",
        email="candidate@example.test",
        location="Dhaka, Bangladesh",
        date_of_birth="1995-04-12",
        full_address="House 10, Dhaka",
        passport_expiry_date="2032-01-14",
        gender="Male",
        nationality="Bangladeshi",
        nid_number="NID-123",
        passport_issue_date="2022-01-15",
    )

    repository.save_profile(profile)
    update_sql, params = next(
        (sql, params) for sql, params in cursor.calls
        if "UPDATE dbo.candidates" in sql
    )

    for field in ("gender", "nationality", "nid_number", "passport_issue_date"):
        assert field in update_sql.lower()
    assert "date_of_birth = ?" in update_sql
    assert "address = ?" in update_sql
    assert len(params) == 23
    assert params[1] == ""
    assert params[4] == date(1995, 4, 12)
    assert params[5] == "House 10, Dhaka"
    assert params[6] == "Dhaka"
    assert params[7] == "Bangladesh"
    assert params[14] == "Male"
    assert params[15] == "Bangladeshi"
    assert params[16] == "NID-123"
    assert params[17] == date(2022, 1, 15)
    assert params[18] == date(2032, 1, 14)
    assert params[-1] == "existing-candidate-id"
    assert connection.committed
