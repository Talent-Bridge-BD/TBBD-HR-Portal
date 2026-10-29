/*
    TBBD HR Portal
    Audit Log Foundation

    Supports:
    - Administrator system activity
    - Authentication events
    - Organization changes
    - Role and permission changes
    - System configuration events
    - Success/failure tracking

    Safe to execute more than once.
*/

SET XACT_ABORT ON;

BEGIN TRANSACTION;

IF OBJECT_ID('dbo.audit_logs', 'U') IS NULL
BEGIN

    CREATE TABLE dbo.audit_logs
    (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_audit_logs PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        user_id NVARCHAR(100) NULL,

        user_email NVARCHAR(320) NULL,

        user_name NVARCHAR(255) NULL,

        organization_id UNIQUEIDENTIFIER NULL,

        event_type NVARCHAR(100) NOT NULL,

        action NVARCHAR(100) NOT NULL,

        entity_type NVARCHAR(100) NULL,

        entity_id NVARCHAR(100) NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_audit_logs_status DEFAULT N'success',

        details NVARCHAR(MAX) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_audit_logs_created_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_audit_logs_organization
            FOREIGN KEY (organization_id)
            REFERENCES dbo.organizations(id),

        CONSTRAINT CK_audit_logs_status
            CHECK (status IN (N'success', N'failure'))
    );

END;

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_audit_logs_created_at'
      AND object_id = OBJECT_ID('dbo.audit_logs')
)
BEGIN
    CREATE INDEX IX_audit_logs_created_at
        ON dbo.audit_logs(created_at DESC);
END;

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_audit_logs_user_id'
      AND object_id = OBJECT_ID('dbo.audit_logs')
)
BEGIN
    CREATE INDEX IX_audit_logs_user_id
        ON dbo.audit_logs(user_id, created_at DESC);
END;

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_audit_logs_organization_id'
      AND object_id = OBJECT_ID('dbo.audit_logs')
)
BEGIN
    CREATE INDEX IX_audit_logs_organization_id
        ON dbo.audit_logs(organization_id, created_at DESC);
END;

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_audit_logs_event_type'
      AND object_id = OBJECT_ID('dbo.audit_logs')
)
BEGIN
    CREATE INDEX IX_audit_logs_event_type
        ON dbo.audit_logs(event_type, created_at DESC);
END;

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_audit_logs_status'
      AND object_id = OBJECT_ID('dbo.audit_logs')
)
BEGIN
    CREATE INDEX IX_audit_logs_status
        ON dbo.audit_logs(status, created_at DESC);
END;

COMMIT TRANSACTION;
