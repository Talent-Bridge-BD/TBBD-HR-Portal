from __future__ import annotations

from repositories.administrator_notifications import (
    AdministratorNotificationRepository,
)


class AdministratorNotificationService:

    def __init__(
        self,
        repository: AdministratorNotificationRepository,
    ):
        self.repository = repository


    def get_email_settings(self):

        return self.repository.get_email_settings()


    def list_templates(self):

        return self.repository.list_templates()


    def list_delivery_logs(
        self,
        limit: int = 100,
    ):

        return self.repository.list_delivery_logs(
            limit=limit
        )