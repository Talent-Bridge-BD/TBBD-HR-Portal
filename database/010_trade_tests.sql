-- Migration 010: Candidate Trade Tests
-- Creates candidate/application-level trade test assessment records.

IF OBJECT_ID('dbo.trade_tests', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.trade_tests (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_trade_tests PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        test_type NVARCHAR(100) NULL,
        scheduled_at DATETIME2(3) NULL,
        location NVARCHAR(500) NULL,
        assessor_name NVARCHAR(200) NULL,

        technical_knowledge_score INT NULL,
        trade_skills_score INT NULL,
        safety_awareness_score INT NULL,
        tool_handling_score INT NULL,
        communication_score INT NULL,
        problem_solving_score INT NULL,
        teamwork_score INT NULL,

        total_score INT NULL,

        result NVARCHAR(30) NOT NULL
            CONSTRAINT DF_trade_tests_result DEFAULT N'Pending',

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_trade_tests_status DEFAULT N'Scheduled',

        assessment_notes NVARCHAR(MAX) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_trade_tests_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_trade_tests_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_trade_tests_application
            FOREIGN KEY (application_id) REFERENCES dbo.applications(id),

        CONSTRAINT CK_trade_tests_result
            CHECK (result IN (N'Pending', N'Pass', N'Fail')),

        CONSTRAINT CK_trade_tests_status
            CHECK (status IN (N'Scheduled', N'Completed', N'Cancelled')),

        CONSTRAINT CK_trade_tests_scores
            CHECK (
                (technical_knowledge_score IS NULL OR technical_knowledge_score BETWEEN 0 AND 100)
                AND (trade_skills_score IS NULL OR trade_skills_score BETWEEN 0 AND 100)
                AND (safety_awareness_score IS NULL OR safety_awareness_score BETWEEN 0 AND 100)
                AND (tool_handling_score IS NULL OR tool_handling_score BETWEEN 0 AND 100)
                AND (communication_score IS NULL OR communication_score BETWEEN 0 AND 100)
                AND (problem_solving_score IS NULL OR problem_solving_score BETWEEN 0 AND 100)
                AND (teamwork_score IS NULL OR teamwork_score BETWEEN 0 AND 100)
                AND (total_score IS NULL OR total_score BETWEEN 0 AND 100)
            )
    );
END
GO
