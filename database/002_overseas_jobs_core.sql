-- TBBD Overseas Recruitment
-- Migration 002: Core overseas job information
--
-- This migration extends the existing dbo.jobs table.
-- Existing jobs and existing recruitment relationships are preserved.

IF COL_LENGTH('dbo.jobs', 'requisition_number') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD requisition_number NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'employer_name') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD employer_name NVARCHAR(250) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'employer_country') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD employer_country NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'employer_city') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD employer_city NVARCHAR(150) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'trade_skill_category') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD trade_skill_category NVARCHAR(150) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'industry_sector') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD industry_sector NVARCHAR(150) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'gender_requirement') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD gender_requirement NVARCHAR(50) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'minimum_age') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD minimum_age INT NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'maximum_age') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD maximum_age INT NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'contract_duration') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD contract_duration NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'work_location') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD work_location NVARCHAR(250) NULL;
END
GO

IF COL_LENGTH('dbo.jobs', 'project_name') IS NULL
BEGIN
    ALTER TABLE dbo.jobs
        ADD project_name NVARCHAR(250) NULL;
END
GO
