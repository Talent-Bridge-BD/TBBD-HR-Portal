/*
    TBBD Employer External Identity mapping table

    REVIEW ONLY. Do not execute against production until separately approved.

    Purpose:
      Link an Entra External ID object (provider + tenant + object ID) to an
      existing canonical dbo.user_profiles.user_id without changing the
      user's existing organization memberships.

    The application_user_id column deliberately matches the verified schema:
      dbo.user_profiles.user_id NVARCHAR(100)
      SQL_Latin1_General_CP1_CI_AS
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF OBJECT_ID(N'dbo.external_identity_mappings', N'U') IS NOT NULL
    THROW 51000, 'dbo.external_identity_mappings already exists; inspect it before applying this migration.', 1;

IF OBJECT_ID(N'dbo.user_profiles', N'U') IS NULL
    THROW 51001, 'dbo.user_profiles does not exist; migration stopped.', 1;

DECLARE @user_id_type sysname;
DECLARE @user_id_length smallint;
DECLARE @user_id_collation sysname;

SELECT
    @user_id_type = TYPE_NAME(c.user_type_id),
    @user_id_length = c.max_length,
    @user_id_collation = c.collation_name
FROM sys.columns AS c
WHERE c.object_id = OBJECT_ID(N'dbo.user_profiles')
  AND c.name = N'user_id';

IF @user_id_type IS NULL
   OR @user_id_type <> N'nvarchar'
   OR @user_id_length <> 200
   OR @user_id_collation <> N'SQL_Latin1_General_CP1_CI_AS'
    THROW 51002, 'dbo.user_profiles.user_id does not match the inspected NVARCHAR(100) schema; migration stopped.', 1;

-- SQL Server requires the referenced foreign-key column to have
-- a single-column primary key or unique key/index.
IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes AS i
    WHERE i.object_id = OBJECT_ID(N'dbo.user_profiles')
      AND i.is_unique = 1
      AND i.is_disabled = 0
      AND i.has_filter = 0
      AND
      (
          SELECT COUNT(*)
          FROM sys.index_columns AS ic
          WHERE ic.object_id = i.object_id
            AND ic.index_id = i.index_id
            AND ic.key_ordinal > 0
      ) = 1
      AND EXISTS
      (
          SELECT 1
          FROM sys.index_columns AS ic
          INNER JOIN sys.columns AS c
              ON c.object_id = ic.object_id
             AND c.column_id = ic.column_id
          WHERE ic.object_id = i.object_id
            AND ic.index_id = i.index_id
            AND ic.key_ordinal = 1
            AND c.name = N'user_id'
      )
)
    THROW 51003, 'dbo.user_profiles.user_id needs a single-column unique key before this migration can proceed.', 1;

BEGIN TRANSACTION;

CREATE TABLE dbo.external_identity_mappings
(
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT DF_external_identity_mappings_id DEFAULT NEWSEQUENTIALID(),
    provider NVARCHAR(100) NOT NULL,
    tenant_id NVARCHAR(100) NOT NULL,
    external_object_id NVARCHAR(200) NOT NULL,
    application_user_id NVARCHAR(100)
        COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
    status NVARCHAR(20) NOT NULL
        CONSTRAINT DF_external_identity_mappings_status DEFAULT N'Pending',
    verified_at DATETIME2(7) NULL,
    verified_by NVARCHAR(100) NULL,
    verification_method NVARCHAR(100) NULL,
    created_at DATETIME2(7) NOT NULL
        CONSTRAINT DF_external_identity_mappings_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(7) NOT NULL
        CONSTRAINT DF_external_identity_mappings_updated_at DEFAULT SYSUTCDATETIME(),

    CONSTRAINT PK_external_identity_mappings PRIMARY KEY CLUSTERED (id),
    CONSTRAINT CK_external_identity_mappings_status
        CHECK (status IN (N'Pending', N'Active', N'Revoked')),
    CONSTRAINT FK_external_identity_mappings_user_profiles
        FOREIGN KEY (application_user_id)
        REFERENCES dbo.user_profiles(user_id)
);

/*
    NVARCHAR key width: 200 + 200 + 400 = 800 bytes, within SQL Server's
    900-byte index key limit. One external identity can map to only one
    application account; one application account may have multiple providers.
*/
CREATE UNIQUE INDEX UX_external_identity_mappings_provider_tenant_object
    ON dbo.external_identity_mappings(provider, tenant_id, external_object_id);

CREATE INDEX IX_external_identity_mappings_application_user
    ON dbo.external_identity_mappings(application_user_id)
    INCLUDE (provider, tenant_id, status);

COMMIT TRANSACTION;
GO
