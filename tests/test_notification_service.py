from unittest.mock import Mock, patch

import pytest

from services.notification_service import NotificationService


def test_notification_service_initializes_without_email_configuration(monkeypatch):
    monkeypatch.delenv("AZURE_COMMUNICATION_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("ACS_EMAIL_CONNECTION_STRING", raising=False)

    with patch(
        "services.notification_service.AdministratorNotificationRepository"
    ):
        service = NotificationService()

    assert service.email_client is None


def test_send_notification_fails_clearly_without_email_configuration(monkeypatch):
    monkeypatch.delenv("AZURE_COMMUNICATION_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("ACS_EMAIL_CONNECTION_STRING", raising=False)

    with patch(
        "services.notification_service.AdministratorNotificationRepository"
    ):
        service = NotificationService()

    with pytest.raises(RuntimeError, match="Email notifications are unavailable"):
        service.send_notification("APPLICATION_RECEIVED", "test@example.com")


def test_notification_service_uses_configured_email_client(monkeypatch):
    monkeypatch.setenv("AZURE_COMMUNICATION_CONNECTION_STRING", "test-connection-string")
    monkeypatch.delenv("ACS_EMAIL_CONNECTION_STRING", raising=False)

    email_client = Mock()

    with (
        patch(
            "services.notification_service.AdministratorNotificationRepository"
        ),
        patch(
            "services.notification_service.EmailClient.from_connection_string",
            return_value=email_client,
        ) as create_client,
    ):
        service = NotificationService()

    create_client.assert_called_once_with("test-connection-string")
    assert service.email_client is email_client
