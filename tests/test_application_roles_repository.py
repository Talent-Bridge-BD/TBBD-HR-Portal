import logging

import pytest

from repositories.application_roles import SqlApplicationRoleRepository


def test_token_acquisition_failure_logs_type_without_secret(monkeypatch, caplog):
    monkeypatch.delenv("WEBSITE_SITE_NAME", raising=False)
    repository = SqlApplicationRoleRepository()

    class FailingCredential:
        def get_token(self, scope):
            raise RuntimeError("access_token=do-not-log-this")

    repository.credential = FailingCredential()

    with caplog.at_level(logging.ERROR, logger="repositories.application_roles"):
        with pytest.raises(RuntimeError, match="do-not-log-this"):
            repository._connection()

    assert "Azure SQL access token acquisition failed" in caplog.text
    assert "RuntimeError" in caplog.text
    assert "do-not-log-this" not in caplog.text
    assert "access_token" not in caplog.text
