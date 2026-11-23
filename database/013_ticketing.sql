-- Migration 013: Candidate Ticketing / Travel
-- Creates application-level travel ticketing records.

IF OBJECT_ID('dbo.ticketing', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.ticketing (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_ticketing PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        airline_name NVARCHAR(200) NULL,
        flight_number NVARCHAR(100) NULL,
        booking_reference NVARCHAR(150) NULL,
        ticket_number NVARCHAR(150) NULL,

        departure_airport NVARCHAR(150) NULL,
        arrival_airport NVARCHAR(150) NULL,

        departure_datetime DATETIME2(3) NULL,
        arrival_datetime DATETIME2(3) NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_ticketing_status DEFAULT N'Pending',

        ticket_document_reference NVARCHAR(500) NULL,
        notes NVARCHAR(MAX) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_ticketing_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_ticketing_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_ticketing_application
            FOREIGN KEY (application_id)
            REFERENCES dbo.applications(id),

        CONSTRAINT CK_ticketing_status
            CHECK (
                status IN (
                    N'Pending',
                    N'Booked',
                    N'Issued',
                    N'Completed',
                    N'Cancelled'
                )
            )
    );
END
GO
