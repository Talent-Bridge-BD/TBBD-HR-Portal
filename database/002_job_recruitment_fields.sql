ALTER TABLE dbo.jobs
ADD
    job_reference NVARCHAR(100) NULL,
    department NVARCHAR(150) NULL,
    job_category NVARCHAR(150) NULL,
    workplace_type NVARCHAR(50) NULL,
    experience NVARCHAR(200) NULL,
    education NVARCHAR(300) NULL,
    skills NVARCHAR(MAX) NULL,
    salary_compensation NVARCHAR(300) NULL,
    application_instructions NVARCHAR(MAX) NULL,
    responsibilities NVARCHAR(MAX) NULL,
    requirements NVARCHAR(MAX) NULL;
GO
