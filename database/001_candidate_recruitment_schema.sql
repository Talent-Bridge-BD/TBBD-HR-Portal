/*
  TBBD HR Portal - Initial Recruitment Data Model
  REVIEW ONLY — DO NOT EXECUTE AGAINST PRODUCTION YET.
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE dbo.organizations (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_organizations PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    name NVARCHAR(200) NOT NULL,
    status NVARCHAR(30) NOT NULL
        CONSTRAINT DF_organizations_status DEFAULT N'active',
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_organizations_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_organizations_updated_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT CK_organizations_status
        CHECK (status IN (N'active', N'inactive', N'suspended')),
    CONSTRAINT UQ_organizations_name UNIQUE (name)
);
GO

CREATE TABLE dbo.organization_memberships (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_organization_memberships PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    organization_id UNIQUEIDENTIFIER NOT NULL,
    user_id NVARCHAR(100) NOT NULL,
    role NVARCHAR(50) NOT NULL,
    status NVARCHAR(30) NOT NULL
        CONSTRAINT DF_organization_memberships_status DEFAULT N'active',
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_organization_memberships_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_organization_memberships_updated_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_organization_memberships_organization
        FOREIGN KEY (organization_id) REFERENCES dbo.organizations(id),
    CONSTRAINT CK_organization_memberships_status
        CHECK (status IN (N'active', N'inactive', N'revoked')),
    CONSTRAINT UQ_organization_memberships_org_user
        UNIQUE (organization_id, user_id)
);
GO

CREATE TABLE dbo.candidates (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_candidates PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    entra_object_id NVARCHAR(100) NOT NULL,
    organization_id UNIQUEIDENTIFIER NULL,
    first_name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(320) NOT NULL,
    phone NVARCHAR(50) NULL,
    date_of_birth DATE NULL,
    address NVARCHAR(500) NULL,
    city NVARCHAR(100) NULL,
    country NVARCHAR(100) NULL,
    professional_summary NVARCHAR(MAX) NULL,
    current_title NVARCHAR(200) NULL,
    years_experience DECIMAL(4,1) NULL,
    profile_status NVARCHAR(30) NOT NULL
        CONSTRAINT DF_candidates_profile_status DEFAULT N'incomplete',
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_candidates_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_candidates_updated_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_candidates_organization
        FOREIGN KEY (organization_id) REFERENCES dbo.organizations(id),
    CONSTRAINT UQ_candidates_entra_object_id UNIQUE (entra_object_id),
    CONSTRAINT CK_candidates_profile_status
        CHECK (profile_status IN (N'incomplete', N'complete', N'under_review', N'verified')),
    CONSTRAINT CK_candidates_years_experience
        CHECK (years_experience IS NULL OR years_experience >= 0)
);
GO

CREATE TABLE dbo.jobs (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_jobs PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    organization_id UNIQUEIDENTIFIER NOT NULL,
    title NVARCHAR(250) NOT NULL,
    description NVARCHAR(MAX) NULL,
    employment_type NVARCHAR(50) NULL,
    location NVARCHAR(200) NULL,
    country NVARCHAR(100) NULL,
    status NVARCHAR(30) NOT NULL
        CONSTRAINT DF_jobs_status DEFAULT N'draft',
    number_of_positions INT NULL,
    published_at DATETIME2(3) NULL,
    closing_at DATETIME2(3) NULL,
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_jobs_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_jobs_updated_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_jobs_organization
        FOREIGN KEY (organization_id) REFERENCES dbo.organizations(id),
    CONSTRAINT CK_jobs_status
        CHECK (status IN (N'draft', N'open', N'paused', N'closed', N'filled', N'cancelled')),
    CONSTRAINT CK_jobs_number_of_positions
        CHECK (number_of_positions IS NULL OR number_of_positions > 0),
    CONSTRAINT CK_jobs_closing_after_published
        CHECK (closing_at IS NULL OR published_at IS NULL OR closing_at > published_at)
);
GO

CREATE TABLE dbo.applications (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_applications PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    candidate_id UNIQUEIDENTIFIER NOT NULL,
    job_id UNIQUEIDENTIFIER NOT NULL,
    status NVARCHAR(30) NOT NULL
        CONSTRAINT DF_applications_status DEFAULT N'submitted',
    cover_letter NVARCHAR(MAX) NULL,
    applied_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_applications_applied_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_applications_updated_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_applications_candidate
        FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
    CONSTRAINT FK_applications_job
        FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),
    CONSTRAINT CK_applications_status
        CHECK (status IN (
            N'submitted', N'under_review', N'shortlisted', N'interview',
            N'offered', N'hired', N'rejected', N'withdrawn'
        )),
    CONSTRAINT UQ_applications_candidate_job
        UNIQUE (candidate_id, job_id)
);
GO

CREATE TABLE dbo.interviews (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_interviews PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    application_id UNIQUEIDENTIFIER NOT NULL,
    scheduled_start DATETIME2(3) NOT NULL,
    scheduled_end DATETIME2(3) NULL,
    interview_type NVARCHAR(50) NULL,
    location_or_link NVARCHAR(500) NULL,
    interviewer_name NVARCHAR(200) NULL,
    notes NVARCHAR(MAX) NULL,
    status NVARCHAR(30) NOT NULL
        CONSTRAINT DF_interviews_status DEFAULT N'scheduled',
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_interviews_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_interviews_updated_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_interviews_application
        FOREIGN KEY (application_id) REFERENCES dbo.applications(id),
    CONSTRAINT CK_interviews_status
        CHECK (status IN (
            N'scheduled', N'completed', N'cancelled', N'rescheduled', N'no_show'
        )),
    CONSTRAINT CK_interviews_end_after_start
        CHECK (scheduled_end IS NULL OR scheduled_end > scheduled_start)
);
GO

CREATE TABLE dbo.documents (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_documents PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    candidate_id UNIQUEIDENTIFIER NOT NULL,
    application_id UNIQUEIDENTIFIER NULL,
    document_type NVARCHAR(50) NOT NULL,
    file_name NVARCHAR(255) NOT NULL,
    blob_container NVARCHAR(100) NOT NULL,
    blob_name NVARCHAR(500) NOT NULL,
    content_type NVARCHAR(100) NULL,
    file_size BIGINT NULL,
    status NVARCHAR(30) NOT NULL
        CONSTRAINT DF_documents_status DEFAULT N'submitted',
    uploaded_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_documents_uploaded_at DEFAULT SYSUTCDATETIME(),
    verified_at DATETIME2(3) NULL,
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_documents_created_at DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_documents_updated_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_documents_candidate
        FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
    CONSTRAINT FK_documents_application
        FOREIGN KEY (application_id) REFERENCES dbo.applications(id),
    CONSTRAINT CK_documents_type
        CHECK (document_type IN (
            N'resume', N'certificate', N'passport', N'identity',
            N'application_document', N'other'
        )),
    CONSTRAINT CK_documents_status
        CHECK (status IN (N'required', N'submitted', N'verified', N'rejected')),
    CONSTRAINT CK_documents_file_size
        CHECK (file_size IS NULL OR file_size >= 0),
    CONSTRAINT UQ_documents_blob
        UNIQUE (blob_container, blob_name)
);
GO

CREATE TABLE dbo.notifications (
    id UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT PK_notifications PRIMARY KEY
        DEFAULT NEWSEQUENTIALID(),
    candidate_id UNIQUEIDENTIFIER NOT NULL,
    type NVARCHAR(50) NOT NULL,
    title NVARCHAR(250) NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    is_read BIT NOT NULL
        CONSTRAINT DF_notifications_is_read DEFAULT 0,
    related_entity_type NVARCHAR(50) NULL,
    related_entity_id UNIQUEIDENTIFIER NULL,
    created_at DATETIME2(3) NOT NULL
        CONSTRAINT DF_notifications_created_at DEFAULT SYSUTCDATETIME(),
    read_at DATETIME2(3) NULL,
    CONSTRAINT FK_notifications_candidate
        FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
    CONSTRAINT CK_notifications_type
        CHECK (type IN (
            N'application_status', N'interview', N'document', N'job', N'system'
        )),
    CONSTRAINT CK_notifications_read_state
        CHECK (
            (is_read = 0 AND read_at IS NULL)
            OR
            (is_read = 1 AND read_at IS NOT NULL)
        )
);
GO

CREATE INDEX IX_candidates_email
    ON dbo.candidates(email);
GO

CREATE INDEX IX_candidates_organization_status
    ON dbo.candidates(organization_id, profile_status);
GO

CREATE INDEX IX_organization_memberships_user_status
    ON dbo.organization_memberships(user_id, status);
GO

CREATE INDEX IX_jobs_organization_status
    ON dbo.jobs(organization_id, status);
GO

CREATE INDEX IX_jobs_status_published
    ON dbo.jobs(status, published_at);
GO

CREATE INDEX IX_applications_candidate_status
    ON dbo.applications(candidate_id, status);
GO

CREATE INDEX IX_applications_job_status
    ON dbo.applications(job_id, status);
GO

CREATE INDEX IX_interviews_application_start
    ON dbo.interviews(application_id, scheduled_start);
GO

CREATE INDEX IX_documents_candidate_type
    ON dbo.documents(candidate_id, document_type);
GO

CREATE INDEX IX_documents_application
    ON dbo.documents(application_id);
GO

CREATE INDEX IX_notifications_candidate_unread_created
    ON dbo.notifications(candidate_id, is_read, created_at DESC);
GO
