/*
    Notification Management Foundation

    Supports:
    - Administrator email configuration
    - Notification templates
    - Delivery logs

    Extends existing dbo.notifications workflow.
*/


-------------------------------------------------
-- Email Configuration
-------------------------------------------------

IF OBJECT_ID('dbo.notification_email_settings', 'U') IS NULL
BEGIN

CREATE TABLE dbo.notification_email_settings
(
    id UNIQUEIDENTIFIER NOT NULL
        DEFAULT NEWID()
        PRIMARY KEY,

    provider NVARCHAR(100) NOT NULL,

    sender_address NVARCHAR(255) NOT NULL,

    sender_name NVARCHAR(255) NULL,

    is_active BIT NOT NULL
        DEFAULT 1,

    created_at DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME(),

    updated_at DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME()
);

END;


-------------------------------------------------
-- Notification Templates
-------------------------------------------------

IF OBJECT_ID('dbo.notification_templates', 'U') IS NULL
BEGIN

CREATE TABLE dbo.notification_templates
(
    id UNIQUEIDENTIFIER NOT NULL
        DEFAULT NEWID()
        PRIMARY KEY,

    template_code NVARCHAR(100) NOT NULL,

    name NVARCHAR(255) NOT NULL,

    event_type NVARCHAR(100) NOT NULL,

    subject NVARCHAR(500) NOT NULL,

    html_body NVARCHAR(MAX) NOT NULL,

    is_active BIT NOT NULL
        DEFAULT 1,

    created_at DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME(),

    updated_at DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME(),

    CONSTRAINT UQ_notification_templates_code
        UNIQUE(template_code)
);

END;


-------------------------------------------------
-- Delivery Logs
-------------------------------------------------

IF OBJECT_ID('dbo.notification_delivery_logs', 'U') IS NULL
BEGIN

CREATE TABLE dbo.notification_delivery_logs
(
    id UNIQUEIDENTIFIER NOT NULL
        DEFAULT NEWID()
        PRIMARY KEY,

    notification_id UNIQUEIDENTIFIER NULL,

    recipient NVARCHAR(255) NOT NULL,

    channel NVARCHAR(50) NOT NULL
        DEFAULT 'EMAIL',

    status NVARCHAR(50) NOT NULL,

    error_message NVARCHAR(MAX) NULL,

    sent_at DATETIME2 NULL,

    created_at DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME()
);

END;