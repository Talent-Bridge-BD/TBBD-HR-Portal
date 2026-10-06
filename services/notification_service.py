import os
from azure.communication.email import EmailClient

from repositories.administrator_notifications import (
    AdministratorNotificationRepository,
)


EMAIL_SENDERS = {
    "APPLICATION_RECEIVED": "applications@talentbridgebd.com",
    "INTERVIEW_SCHEDULED": "interviews@talentbridgebd.com",
    "OFFER_CREATED": "offers@talentbridgebd.com",
    "OFFER_SENT": "offers@talentbridgebd.com",
    "HR_NOTIFICATION": "hr@talentbridgebd.com",
    "SECURITY_ALERT": "security@talentbridgebd.com",
    "DEFAULT": "notifications@talentbridgebd.com",
}


class NotificationService:

    def __init__(self):
        self.repository = AdministratorNotificationRepository()

        self.email_client = EmailClient.from_connection_string(
            os.environ["AZURE_COMMUNICATION_CONNECTION_STRING"]
        )


    def send_notification(
        self,
        event_type: str,
        recipient: str,
        subject_data: dict | None = None,
    ):

        templates = self.repository.list_templates()

        template = next(
            (
                item
                for item in templates
                if item["event_type"] == event_type
            ),
            None,
        )

        if not template:
            raise ValueError(
                f"No notification template found for {event_type}"
            )


        subject = template["subject"]

        if subject_data:
            for key, value in subject_data.items():
                subject = subject.replace(
                    "{{" + key + "}}",
                    str(value),
                )


        delivery_log = self.repository.create_delivery_log(
            recipient=recipient,
            channel="EMAIL",
            status="PENDING",
            notification_id=None,
        )

        try:
            sender = EMAIL_SENDERS.get(
                event_type,
                EMAIL_SENDERS["DEFAULT"],
            )

            poller = self.email_client.begin_send(
                {
                    "senderAddress": sender,
                    "recipients": {
                        "to": [
                            {
                                "address": recipient,
                            }
                        ]
                    },
                    "content": {
                        "subject": subject,
                        "plainText": subject,
                    },
                }
            )

            result = poller.result()

            print(f"[ACS EMAIL] {result}")

            if result["status"] == "Succeeded":
                self.repository.update_delivery_status(
                    delivery_log["id"],
                    "SENT",
                )
            else:
                self.repository.update_delivery_status(
                    delivery_log["id"],
                    "FAILED",
                    str(result),
                )

        except Exception as email_error:
            print(f"[ACS EMAIL ERROR] {email_error}")

            self.repository.update_delivery_status(
                delivery_log["id"],
                "FAILED",
                str(email_error),
            )

        return delivery_log
