-- Candidate Profile V1
-- Reuses dbo.candidates and dbo.documents.
-- Adds supporting candidate-owned profile entities.

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE object_id = OBJECT_ID(N'dbo.candidate_skills')
)
BEGIN
    CREATE TABLE dbo.candidate_skills (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_candidate_skills PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),
        candidate_id UNIQUEIDENTIFIER NOT NULL,
        skill_name NVARCHAR(150) NOT NULL,
        skill_category NVARCHAR(50) NULL,
        proficiency NVARCHAR(30) NULL,
        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_skills_created_at DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_skills_updated_at DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_candidate_skills_candidate
            FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
        CONSTRAINT CK_candidate_skills_name
            CHECK (LEN(LTRIM(RTRIM(skill_name))) > 0),
        CONSTRAINT CK_candidate_skills_proficiency
            CHECK (
                proficiency IS NULL
                OR proficiency IN (
                    N'beginner',
                    N'intermediate',
                    N'advanced',
                    N'expert'
                )
            )
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE object_id = OBJECT_ID(N'dbo.candidate_experience')
)
BEGIN
    CREATE TABLE dbo.candidate_experience (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_candidate_experience PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),
        candidate_id UNIQUEIDENTIFIER NOT NULL,
        job_title NVARCHAR(200) NOT NULL,
        company NVARCHAR(200) NOT NULL,
        location NVARCHAR(200) NULL,
        employment_type NVARCHAR(50) NULL,
        start_date DATE NOT NULL,
        end_date DATE NULL,
        currently_working BIT NOT NULL
            CONSTRAINT DF_candidate_experience_currently_working DEFAULT 0,
        description NVARCHAR(MAX) NULL,
        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_experience_created_at DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_experience_updated_at DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_candidate_experience_candidate
            FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
        CONSTRAINT CK_candidate_experience_dates
            CHECK (end_date IS NULL OR end_date >= start_date),
        CONSTRAINT CK_candidate_experience_current
            CHECK (
                (currently_working = 1 AND end_date IS NULL)
                OR
                (currently_working = 0)
            )
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE object_id = OBJECT_ID(N'dbo.candidate_education')
)
BEGIN
    CREATE TABLE dbo.candidate_education (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_candidate_education PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),
        candidate_id UNIQUEIDENTIFIER NOT NULL,
        degree_qualification NVARCHAR(200) NOT NULL,
        institution NVARCHAR(250) NOT NULL,
        field_of_study NVARCHAR(200) NULL,
        start_date DATE NULL,
        end_date DATE NULL,
        description NVARCHAR(MAX) NULL,
        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_education_created_at DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_education_updated_at DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_candidate_education_candidate
            FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
        CONSTRAINT CK_candidate_education_dates
            CHECK (
                start_date IS NULL
                OR end_date IS NULL
                OR end_date >= start_date
            )
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE object_id = OBJECT_ID(N'dbo.candidate_certifications')
)
BEGIN
    CREATE TABLE dbo.candidate_certifications (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_candidate_certifications PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),
        candidate_id UNIQUEIDENTIFIER NOT NULL,
        certification_name NVARCHAR(250) NOT NULL,
        issuing_organization NVARCHAR(250) NOT NULL,
        issue_date DATE NULL,
        expiry_date DATE NULL,
        credential_id NVARCHAR(150) NULL,
        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_certifications_created_at DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_certifications_updated_at DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_candidate_certifications_candidate
            FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
        CONSTRAINT CK_candidate_certifications_dates
            CHECK (
                issue_date IS NULL
                OR expiry_date IS NULL
                OR expiry_date >= issue_date
            )
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE object_id = OBJECT_ID(N'dbo.candidate_preferences')
)
BEGIN
    CREATE TABLE dbo.candidate_preferences (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_candidate_preferences PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),
        candidate_id UNIQUEIDENTIFIER NOT NULL,
        preferred_job_title NVARCHAR(200) NULL,
        preferred_location NVARCHAR(200) NULL,
        preferred_employment_type NVARCHAR(50) NULL,
        work_arrangement NVARCHAR(30) NULL,
        expected_salary DECIMAL(18,2) NULL,
        currency NVARCHAR(10) NULL,
        availability_notice_period NVARCHAR(100) NULL,
        open_to_relocation BIT NULL,
        available_for_recruitment BIT NOT NULL
            CONSTRAINT DF_candidate_preferences_available_for_recruitment DEFAULT 1,
        preferred_contact_method NVARCHAR(30) NULL,
        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_preferences_created_at DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_preferences_updated_at DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_candidate_preferences_candidate
            FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
        CONSTRAINT UQ_candidate_preferences_candidate
            UNIQUE (candidate_id),
        CONSTRAINT CK_candidate_preferences_salary
            CHECK (expected_salary IS NULL OR expected_salary >= 0),
        CONSTRAINT CK_candidate_preferences_work_arrangement
            CHECK (
                work_arrangement IS NULL
                OR work_arrangement IN (
                    N'on_site',
                    N'hybrid',
                    N'remote'
                )
            ),
        CONSTRAINT CK_candidate_preferences_contact_method
            CHECK (
                preferred_contact_method IS NULL
                OR preferred_contact_method IN (
                    N'email',
                    N'phone'
                )
            )
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE parent_object_id = OBJECT_ID(N'dbo.documents')
      AND name = N'CK_documents_type'
      AND definition LIKE N'%identification%'
)
BEGIN
    ALTER TABLE dbo.documents
        DROP CONSTRAINT CK_documents_type;

    ALTER TABLE dbo.documents
        ADD CONSTRAINT CK_documents_type
        CHECK (document_type IN (
            N'resume',
            N'certificate',
            N'passport',
            N'identity',
            N'identification',
            N'application_document',
            N'other'
        ));
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'dbo.candidate_skills')
      AND name = N'IX_candidate_skills_candidate'
)
BEGIN
    CREATE INDEX IX_candidate_skills_candidate
        ON dbo.candidate_skills(candidate_id);
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'dbo.candidate_experience')
      AND name = N'IX_candidate_experience_candidate'
)
BEGIN
    CREATE INDEX IX_candidate_experience_candidate
        ON dbo.candidate_experience(candidate_id, start_date DESC);
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'dbo.candidate_education')
      AND name = N'IX_candidate_education_candidate'
)
BEGIN
    CREATE INDEX IX_candidate_education_candidate
        ON dbo.candidate_education(candidate_id, start_date DESC);
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'dbo.candidate_certifications')
      AND name = N'IX_candidate_certifications_candidate'
)
BEGIN
    CREATE INDEX IX_candidate_certifications_candidate
        ON dbo.candidate_certifications(candidate_id, issue_date DESC);
END;
GO
