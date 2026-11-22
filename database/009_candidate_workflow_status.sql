ALTER TABLE dbo.candidates
ADD workflow_status NVARCHAR(50) NOT NULL
    CONSTRAINT DF_candidates_workflow_status
    DEFAULT N'Applied';
GO

ALTER TABLE dbo.candidates
ADD CONSTRAINT CK_candidates_workflow_status
CHECK (
    workflow_status IN (
        N'Applied',
        N'Screening',
        N'Interview',
        N'Trade Test',
        N'Medical',
        N'Visa Processing',
        N'Ticketing',
        N'Onboarding',
        N'Deployment',
        N'Completed'
    )
);
GO
