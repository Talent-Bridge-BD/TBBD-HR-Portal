from repositories.administrator_notifications import (
    AdministratorNotificationRepository,
)


class NotificationService:

    def __init__(self):
        self.repository = AdministratorNotificationRepository()


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


        return self.repository.create_delivery_log(
            recipient=recipient,
            channel="EMAIL",
            status="PENDING",
            notification_id=None,
        )
