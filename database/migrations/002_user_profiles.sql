CREATE TABLE dbo.user_profiles (
    user_id NVARCHAR(100) NOT NULL
        CONSTRAINT PK_user_profiles PRIMARY KEY,
    full_name NVARCHAR(200) NULL,
    phone NVARCHAR(50) NULL,
    organization_email NVARCHAR(320) NULL,
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_user_profiles_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_user_profiles_updated_at DEFAULT SYSUTCDATETIME()
);
GO
