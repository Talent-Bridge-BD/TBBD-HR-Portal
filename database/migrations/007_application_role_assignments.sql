/*
  TBBD HR Portal - Application-managed role assignments
  REVIEW ONLY — DO NOT EXECUTE AGAINST PRODUCTION.
  Candidate role assignment is separate from approval status.
*/
IF OBJECT_ID(N'dbo.application_role_assignments', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.application_role_assignments (
        id UNIQUEIDENTIFIER NOT NULL
            PRIMARY KEY DEFAULT NEWSEQUENTIALID(),
        user_id NVARCHAR(200) NOT NULL,
        role NVARCHAR(50) NOT NULL,
        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_application_role_assignments_status
            DEFAULT N'active',
        assigned_by NVARCHAR(200) NULL,
        created_at DATETIME2(3) NOT NULL
            DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_application_role_assignments_user_role
            UNIQUE (user_id, role),
        CONSTRAINT CK_application_role_assignments_status
            CHECK (status IN (N'active', N'inactive', N'revoked'))
    );
END;
GO
