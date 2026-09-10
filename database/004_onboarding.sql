/*
  TBBD HR Portal - Onboarding V1
  Safe migration — does not recreate an existing table or indexes.
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.onboarding', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.onboarding (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_onboarding PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_onboarding_status DEFAULT N'pending',

        planned_start_date DATE NULL,

        employment_type NVARCHAR(50) NULL,

        notes NVARCHAR(MAX) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_onboarding_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_onboarding_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_onboarding_application
            FOREIGN KEY (application_id)
            REFERENCES dbo.applications(id),

        CONSTRAINT CK_onboarding_status
            CHECK (
                status IN (
                    N'pending',
                    N'in_progress',
                    N'completed',
                    N'cancelled'
                )
            )
    );
END;
GO

IF OBJECT_ID(N'dbo.onboarding', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE name = N'IX_onboarding_application'
         AND object_id = OBJECT_ID(N'dbo.onboarding')
   )
BEGIN
    CREATE INDEX IX_onboarding_application
        ON dbo.onboarding(application_id, created_at DESC);
END;
GO

IF OBJECT_ID(N'dbo.onboarding', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE name = N'IX_onboarding_status'
         AND object_id = OBJECT_ID(N'dbo.onboarding')
   )
BEGIN
    CREATE INDEX IX_onboarding_status
        ON dbo.onboarding(status, updated_at DESC);
END;
GO
