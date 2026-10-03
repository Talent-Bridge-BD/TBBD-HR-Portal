from __future__ import annotations

from repositories.notifications import (
    NotificationRepository,
)


class NotificationService:

    def __init__(
        self,
        repository: NotificationRepository,
    ):
        self.repository = repository

    def list_notifications(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
        limit: int = 50,
    ) -> list[dict]:

        return self.repository.list_for_recipient(
            recipient_user_id=recipient_user_id,
            organization_ids=organization_ids,
            limit=limit,
        )

    def unread_count(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
    ) -> int:

        return self.repository.count_unread(
            recipient_user_id=recipient_user_id,
            organization_ids=organization_ids,
        )

    def mark_read(
        self,
        notification_id: str,
        recipient_user_id: str,
    ) -> dict | None:

        return self.repository.mark_read(
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )

    def mark_all_read(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
    ) -> int:

        return self.repository.mark_all_read(
            recipient_user_id=recipient_user_id,
            organization_ids=organization_ids,
        )

    def create(
        self,
        *,
        candidate_id: str,
        recipient_user_id: str,
        recipient_type: str,
        title: str,
        message: str,
        notification_type: str,
        event_type: str,
        organization_id: str | None = None,
        application_id: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> dict:

        return self.repository.create(
            candidate_id=candidate_id,
            recipient_user_id=recipient_user_id,
            recipient_type=recipient_type,
            title=title,
            message=message,
            notification_type=notification_type,
            event_type=event_type,
            organization_id=organization_id,
            application_id=application_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
