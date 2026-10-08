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
                and item["is_active"]
            ),
            None,
        )

        if not template:
            raise ValueError(
                f"No active notification template found for {event_type}"
            )

        import html as html_module
        import re

        subject = template["subject"]
        html_body = template.get("html_body") or ""

        if subject_data:
            for key, value in subject_data.items():
                placeholder = "{{" + key + "}}"
                value_text = str(value)
                subject = subject.replace(placeholder, value_text)
                html_body = html_body.replace(
                    placeholder,
                    html_module.escape(value_text),
                )

        plain_text = re.sub(
            r"\s+",
            " ",
            html_module.unescape(
                re.sub(r"<[^>]+>", " ", html_body)
            ),
        ).strip() or subject


        delivery_log = self.repository.create_delivery_log(
            recipient=recipient,
            channel="EMAIL",
            status="PENDING",
            notification_id=None,
        )

        final_status = "PENDING"

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
                        "plainText": plain_text,
                        "html": html_body,
                    },
                }
            )

            result = poller.result()

            print(f"[ACS EMAIL] {result}")

            if result["status"] == "Succeeded":
                final_status = "SENT"
                self.repository.update_delivery_status(
                    delivery_log["id"],
                    "SENT",
                )
            else:
                final_status = "FAILED"
                self.repository.update_delivery_status(
                    delivery_log["id"],
                    "FAILED",
                    str(result),
                )

        except Exception as email_error:
            final_status = "FAILED"
            print(f"[ACS EMAIL ERROR] {email_error}")

            self.repository.update_delivery_status(
                delivery_log["id"],
                "FAILED",
                str(email_error),
            )

        return {
            **delivery_log,
            "status": final_status,
        }
