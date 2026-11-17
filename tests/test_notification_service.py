import pytest

import services.notification_service as notification_service


class FakeRepository:
    def __init__(self):
        self.updates = []
        self.created_log = None

    def list_templates(self):
        return [
            {
                "event_type": "INTERVIEW_SCHEDULED",
                "is_active": True,
                "subject": "Interview for {{candidate_name}}",
                "html_body": "<p>Hello {{candidate_name}}</p>",
            }
        ]

    def create_delivery_log(
        self, recipient, channel, status, notification_id=None
    ):
        self.created_log = {
            "id": "delivery-test-001",
            "recipient": recipient,
            "channel": channel,
            "status": status,
            "notification_id": notification_id,
        }
        return self.created_log

    def update_delivery_status(
        self, delivery_id, status, error_message=None
    ):
        self.updates.append(
            {
                "delivery_id": delivery_id,
                "status": status,
                "error_message": error_message,
            }
        )


class FakePoller:
    def result(self):
        return {"status": "Succeeded"}


class FakeEmailClient:
    def begin_send(self, message):
        self.message = message
        return FakePoller()


def configure_service(monkeypatch, repository, email_client):
    monkeypatch.setattr(
        notification_service,
        "AdministratorNotificationRepository",
        lambda: repository,
    )
    monkeypatch.setattr(
        notification_service.EmailClient,
        "from_connection_string",
        lambda connection_string: email_client,
    )
    monkeypatch.setenv(
        "AZURE_COMMUNICATION_CONNECTION_STRING",
        "mock-connection-string",
    )


def test_send_notification_records_success_without_real_email(monkeypatch):
    repository = FakeRepository()
    email_client = FakeEmailClient()
    configure_service(monkeypatch, repository, email_client)

    service = notification_service.NotificationService()
    result = service.send_notification(
        event_type="INTERVIEW_SCHEDULED",
        recipient="candidate@example.test",
        subject_data={"candidate_name": "Test Candidate"},
    )

    assert result["status"] == "SENT"
    assert repository.created_log["notification_id"] is None
    assert repository.updates == [
        {
            "delivery_id": "delivery-test-001",
            "status": "SENT",
            "error_message": None,
        }
    ]
    assert email_client.message["content"]["subject"] == (
        "Interview for Test Candidate"
    )
    assert email_client.message["content"]["plainText"] == "Hello Test Candidate"


def test_send_notification_records_provider_failure(monkeypatch):
    repository = FakeRepository()

    class FailingEmailClient:
        def begin_send(self, message):
            raise RuntimeError("Simulated provider failure")

    configure_service(monkeypatch, repository, FailingEmailClient())

    service = notification_service.NotificationService()
    result = service.send_notification(
        event_type="INTERVIEW_SCHEDULED",
        recipient="candidate@example.test",
        subject_data={"candidate_name": "Test Candidate"},
    )

    assert result["status"] == "FAILED"
    assert repository.updates == [
        {
            "delivery_id": "delivery-test-001",
            "status": "FAILED",
            "error_message": "Simulated provider failure",
        }
    ]


def test_strip_html_tags_preserves_normal_and_malformed_text():
    assert notification_service._strip_html_tags(
        "<p>Hello</p> <strong>Candidate</strong>"
    ) == " Hello   Candidate "
    assert notification_service._strip_html_tags(
        "Hello <unfinished"
    ) == "Hello <unfinished"


def test_strip_html_tags_handles_repeated_opening_brackets_linearly():
    repeated_opening_brackets = "<" * 200_000

    assert notification_service._strip_html_tags(
        repeated_opening_brackets
    ) == repeated_opening_brackets


def test_strip_html_tags_removes_a_tag_after_repeated_opening_brackets():
    value = "<" * 200_000 + "<p>safe</p>"

    assert notification_service._strip_html_tags(value) == " safe "


def test_send_notification_rejects_oversized_template(monkeypatch):
    repository = FakeRepository()
    repository.list_templates = lambda: [{
        "event_type": "INTERVIEW_SCHEDULED",
        "is_active": True,
        "subject": "Interview",
        "html_body": "<p>" + "x" * notification_service.MAX_NOTIFICATION_HTML_LENGTH,
    }]
    email_client = FakeEmailClient()
    configure_service(monkeypatch, repository, email_client)

    service = notification_service.NotificationService()
    with pytest.raises(ValueError, match="supported length"):
        service.send_notification(
            event_type="INTERVIEW_SCHEDULED",
            recipient="candidate@example.test",
        )

    assert repository.created_log is None
