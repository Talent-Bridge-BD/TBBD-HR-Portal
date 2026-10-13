IF OBJECT_ID(N'dbo.employer_access_requests', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.employer_access_requests (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT DF_employer_access_requests_id DEFAULT NEWID(),
        company_name NVARCHAR(200) NOT NULL,
        representative_name NVARCHAR(200) NOT NULL,
        email NVARCHAR(320) NOT NULL,
        phone NVARCHAR(50) NULL,
        country NVARCHAR(100) NULL,
        industry NVARCHAR(150) NULL,
        requested_roles NVARCHAR(1000) NULL,
        requirements NVARCHAR(MAX) NULL,
        status NVARCHAR(20) NOT NULL
            CONSTRAINT DF_employer_access_requests_status DEFAULT N'Pending',
        reviewed_by NVARCHAR(320) NULL,
        reviewed_at DATETIME2(3) NULL,
        review_notes NVARCHAR(2000) NULL,
        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_employer_access_requests_created_at
            DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_employer_access_requests_updated_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_employer_access_requests
            PRIMARY KEY (id),
        CONSTRAINT CK_employer_access_requests_status
            CHECK (status IN (N'Pending', N'Approved', N'Rejected'))
    );

    CREATE INDEX IX_employer_access_requests_status_created_at
        ON dbo.employer_access_requests (status, created_at DESC);
END;