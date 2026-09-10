/*
  TBBD HR Portal - Offers
  Safe migration — does not recreate an existing table or index.
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.offers', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.offers (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_offers PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        offer_date DATETIME2(3) NOT NULL
            CONSTRAINT DF_offers_offer_date DEFAULT SYSUTCDATETIME(),

        expiry_date DATETIME2(3) NULL,

        start_date DATE NULL,

        employment_type NVARCHAR(50) NULL,

        salary_compensation NVARCHAR(200) NULL,

        currency NVARCHAR(10) NULL,

        location NVARCHAR(200) NULL,

        notes NVARCHAR(MAX) NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_offers_status DEFAULT N'draft',

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_offers_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_offers_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_offers_application
            FOREIGN KEY (application_id)
            REFERENCES dbo.applications(id),

        CONSTRAINT CK_offers_status
            CHECK (status IN (
                N'draft',
                N'sent',
                N'accepted',
                N'declined',
                N'expired',
                N'withdrawn'
            )),

        CONSTRAINT CK_offers_expiry_after_offer
            CHECK (
                expiry_date IS NULL
                OR expiry_date > offer_date
            ),

        CONSTRAINT CK_offers_start_date
            CHECK (
                start_date IS NULL
                OR start_date >= CAST(offer_date AS DATE)
            )
    );
END;
GO

IF OBJECT_ID(N'dbo.offers', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE name = N'IX_offers_application'
         AND object_id = OBJECT_ID(N'dbo.offers')
   )
BEGIN
    CREATE INDEX IX_offers_application
        ON dbo.offers(application_id, offer_date DESC);
END;
GO

IF OBJECT_ID(N'dbo.offers', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE name = N'IX_offers_status'
         AND object_id = OBJECT_ID(N'dbo.offers')
   )
BEGIN
    CREATE INDEX IX_offers_status
        ON dbo.offers(status, updated_at DESC);
END;
GO
