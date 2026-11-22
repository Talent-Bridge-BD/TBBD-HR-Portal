/*
    TBBD HR Portal
    Notification Foundation Migration

    Purpose:
      Evolve the existing dbo.notifications table to support:
        - Candidate notifications
        - Employer/HR notifications
        - Organization scoping
        - Application scoping
        - Machine-readable business events

    Safety:
      - Does NOT create a second notifications table.
      - Preserves existing notification rows.
      - Safe to execute more than once.
*/

SET XACT_ABORT ON;

BEGIN TRANSACTION;

------------------------------------------------------------
-- 1. Recipient identity
------------------------------------------------------------

IF COL_LENGTH('dbo.notifications', 'recipient_user_id') IS NULL
BEGIN
    ALTER TABLE dbo.notifications
        ADD recipient_user_id NVARCHAR(100) NULL;
END;

------------------------------------------------------------
-- 2. Recipient type
------------------------------------------------------------

IF COL_LENGTH('dbo.notifications', 'recipient_type') IS NULL
BEGIN
    ALTER TABLE dbo.notifications
        ADD recipient_type NVARCHAR(30) NULL;
END;

------------------------------------------------------------
-- 3. Organization context
------------------------------------------------------------

IF COL_LENGTH('dbo.notifications', 'organization_id') IS NULL
BEGIN
    ALTER TABLE dbo.notifications
        ADD organization_id UNIQUEIDENTIFIER NULL;
END;

------------------------------------------------------------
-- 4. Application context
------------------------------------------------------------

IF COL_LENGTH('dbo.notifications', 'application_id') IS NULL
BEGIN
    ALTER TABLE dbo.notifications
        ADD application_id UNIQUEIDENTIFIER NULL;
END;

------------------------------------------------------------
-- 5. Exact business event
------------------------------------------------------------

IF COL_LENGTH('dbo.notifications', 'event_type') IS NULL
BEGIN
    ALTER TABLE dbo.notifications
        ADD event_type NVARCHAR(80) NULL;
END;

------------------------------------------------------------
-- 6. Recipient type integrity
------------------------------------------------------------

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'CK_notifications_recipient_type'
      AND parent_object_id = OBJECT_ID('dbo.notifications')
)
BEGIN
    ALTER TABLE dbo.notifications
        ADD CONSTRAINT CK_notifications_recipient_type
        CHECK (
            recipient_type IS NULL
            OR recipient_type IN (
                N'candidate',
                N'employer',
                N'hr'
            )
        );
END;

------------------------------------------------------------
-- 7. Organization foreign key
------------------------------------------------------------

IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'FK_notifications_organization'
      AND parent_object_id = OBJECT_ID('dbo.notifications')
)
BEGIN
    ALTER TABLE dbo.notifications
        ADD CONSTRAINT FK_notifications_organization
        FOREIGN KEY (organization_id)
        REFERENCES dbo.organizations(id);
END;

------------------------------------------------------------
-- 8. Application foreign key
------------------------------------------------------------

IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'FK_notifications_application'
      AND parent_object_id = OBJECT_ID('dbo.notifications')
)
BEGIN
    ALTER TABLE dbo.notifications
        ADD CONSTRAINT FK_notifications_application
        FOREIGN KEY (application_id)
        REFERENCES dbo.applications(id);
END;

------------------------------------------------------------
-- 9. Recipient / unread lookup
------------------------------------------------------------

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_notifications_recipient_unread_created'
      AND object_id = OBJECT_ID('dbo.notifications')
)
BEGIN
    CREATE INDEX IX_notifications_recipient_unread_created
        ON dbo.notifications
        (
            recipient_user_id,
            is_read,
            created_at DESC
        );
END;

------------------------------------------------------------
-- 10. Organization lookup
------------------------------------------------------------

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_notifications_organization_created'
      AND object_id = OBJECT_ID('dbo.notifications')
)
BEGIN
    CREATE INDEX IX_notifications_organization_created
        ON dbo.notifications
        (
            organization_id,
            created_at DESC
        );
END;

------------------------------------------------------------
-- 11. Application lookup
------------------------------------------------------------

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_notifications_application_created'
      AND object_id = OBJECT_ID('dbo.notifications')
)
BEGIN
    CREATE INDEX IX_notifications_application_created
        ON dbo.notifications
        (
            application_id,
            created_at DESC
        );
END;

COMMIT TRANSACTION;
