TBBD HR Portal

«The Talent Bridge BD Human Resources platform — a modern web application for recruitment, candidate and employer access, and internal HR operations, built with React, FastAPI, and Microsoft Azure services.»

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react&logoColor=white" alt="React 19">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/Node.js-20-339933?logo=nodedotjs&logoColor=white" alt="Node.js 20">
  <img src="https://img.shields.io/badge/Identity-Microsoft%20Entra%20ID-5C2D91?logo=microsoftentra&logoColor=white" alt="Microsoft Entra ID">
  <img src="https://img.shields.io/badge/Cloud-Microsoft%20Azure-0078D4?logo=microsoftazure&logoColor=white" alt="Microsoft Azure">
  <img src="https://img.shields.io/badge/CI-Azure%20DevOps%20%7C%20GitHub%20Actions-2088FF?logo=githubactions&logoColor=white" alt="Continuous Integration">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>---

Welcome

Welcome to the TBBD HR Portal repository.

The TBBD HR Portal is the Human Resources application developed for Talent Bridge BD (TBBD), a workforce and recruitment solutions initiative of Loyal Trade Management Ltd.

The platform provides a centralized digital environment for candidate services, employer access, recruitment workflows, and internal HR operations.

The repository contains the application source code, frontend, backend API services, data-access components, automated tests, CI validation workflows, and technical documentation.

The application is designed around role-aware access, backend-enforced authorization, and integration with Microsoft Azure services.

---

Table of Contents

- "Repository Information" (#repository-information)
- "Overview" (#overview)
- "Vision" (#vision)
- "Objectives" (#objectives)
- "Key Capabilities" (#key-capabilities)
  - "Candidate Portal" (#candidate-portal)
  - "Employer Portal" (#employer-portal)
  - "Internal HR Operations" (#internal-hr-operations)
  - "Recruitment and Processing" (#recruitment-and-processing)
- "Technology Stack" (#technology-stack)
- "Application Architecture" (#application-architecture)
- "AI-Assisted Policy Capabilities" (#ai-assisted-policy-capabilities)
- "Repository Structure" (#repository-structure)
- "Documentation" (#documentation)
- "Getting Started" (#getting-started)
- "Configuration and Security" (#configuration-and-security)
- "Continuous Integration and Validation" (#continuous-integration-and-validation)
- "Container Build" (#container-build)
- "Current Project Status" (#current-project-status)
- "Development Guidelines" (#development-guidelines)
- "Support" (#support)
- "License" (#license)

---

Repository Information

Property| Value
Project| TBBD HR Portal
Organization| Talent Bridge BD (TBBD)
Repository| TBBD-HR-Portal
Version| Active Development
Project Status| Active Development
Frontend| React 19 / Vite
Backend| Python 3.11 / FastAPI
Cloud Platform| Microsoft Azure
Identity Platform| Microsoft Entra ID and configured external identity authentication
Database| Azure SQL / SQL Server
Source Control| GitHub
CI Platform| Azure DevOps Pipelines / GitHub Actions
Maintained By| Talent Bridge BD Technology Team
License| MIT

---

Overview

The TBBD HR Portal is designed to modernize recruitment and Human Resources operations through a secure, role-aware web application.

The platform combines:

- Modern React-based user experiences.
- FastAPI backend services.
- Microsoft identity integrations.
- Backend-enforced role-based authorization.
- Candidate registration and profile management.
- Employer access and organization-related operations.
- Recruitment and application workflows.
- Internal HR and administrative operations.
- Azure SQL database connectivity.
- Azure service integrations.
- AI-assisted policy-search capabilities.
- Automated testing and continuous integration validation.

The application follows a modular architecture that separates frontend presentation, identity authentication, backend authorization, business logic, and data-access operations.

This repository serves as the primary source for application code, technical implementation, automated validation, and supporting documentation.

---

Vision

To build a secure, intelligent, scalable, and modern Human Resources platform that connects Bangladeshi talent with global employment opportunities while supporting employers and internal HR operations.

The TBBD HR Portal aims to provide a connected digital workplace that simplifies recruitment, strengthens workforce management, and supports efficient collaboration between candidates, employers, and HR personnel.

---

Objectives

The TBBD HR Portal aims to:

- Modernize Human Resources operations.
- Improve candidate access and profile management.
- Simplify employer access and recruitment workflows.
- Support secure workplace access.
- Strengthen identity and authorization controls.
- Improve recruitment and hiring processes.
- Support document and application management.
- Enable AI-assisted workplace capabilities.
- Maintain enterprise security and governance.
- Promote maintainable software development.
- Improve automated testing and validation.
- Establish a scalable foundation for future workforce solutions.

---

Key Capabilities

Candidate Portal

Designed to support candidate-facing operations, including:

- Candidate registration and authentication.
- Candidate profile management.
- Personal and professional information.
- Document management.
- Job application workflows.
- Application status and recruitment processing.
- Candidate information and profile validation.
- Recruitment-related communication and processing.

Candidate access and recruitment functionality are subject to applicable profile completion, approval, and authorization requirements.

Employer Portal

Designed to support employer-facing operations, including:

- Employer access requests.
- Employer authentication and authorized access.
- Organization-related operations.
- Employer dashboard.
- Job and vacancy management.
- Recruitment requests and workflows.
- Candidate application management.
- Employer-related recruitment operations.

Employer-facing functionality is under active development and validation. Individual modules and dashboard operations may have different implementation and operational statuses.

Internal HR Operations

Supports internal HR personnel and administrators through authenticated access to the TBBD HR Portal.

Internal capabilities include:

- Staff and administrator authentication.
- Role-based application permissions.
- Organization management.
- Candidate approval workflows.
- Recruitment administration.
- Candidate and employer management.
- Internal HR operational capabilities.
- Administrative dashboard functionality.
- Application and access management.

These capabilities are provided within the TBBD HR Portal and do not represent a separate Employee Portal application.

Recruitment and Processing

The backend contains API modules supporting recruitment and workforce processing areas such as:

- Job management.
- Recruitment and job requests.
- Applications.
- Candidate screening.
- Interviews.
- Trade tests.
- Medical examinations.
- Visa processing.
- Ticketing.
- Onboarding.
- Deployment and recruitment pipeline operations.

The presence of an API module does not, by itself, establish that every workflow is fully implemented, integrated, or operational in production.

---

Technology Stack

The application uses a combination of modern frontend technologies, Python backend services, Microsoft identity technologies, and Azure cloud services.

Area| Technology
Frontend Framework| React 19
Frontend Build Tool| Vite
Frontend Runtime and Build| Node.js 20 / npm
Browser Authentication| Microsoft Authentication Library (MSAL Browser)
Backend Language| Python 3.11
API Framework| FastAPI
API Server| Uvicorn
Identity Platform| Microsoft Entra ID and configured external identity authentication
Authentication| MSAL Browser and Microsoft identity integrations
Authorization| Application-level, backend-enforced role-based access control
Database| Azure SQL / SQL Server
Database Connectivity| pyodbc
Azure Identity| Azure Identity SDK
File Storage| Azure Storage SDK
Artificial Intelligence| Azure OpenAI SDK
Knowledge Retrieval| Azure AI Search
Email Services| Azure Communication Services Email SDK
PDF Generation| ReportLab
Containerization| Docker
Source Control| GitHub
CI Validation| Azure DevOps Pipelines / GitHub Actions

The availability of individual integrations depends on application configuration, credentials, permissions, and the corresponding Azure service resources.

---

Application Architecture

The TBBD HR Portal follows a layered application architecture that separates user authentication, backend authorization, role-specific API operations, business logic, and data access.

High-Level Architecture

                    Application Users
                           |
                           v
                    React 19 / Vite
                           |
                           v
                 Identity Authentication
                           |
              +------------+------------+
              |                         |
              v                         v
       Microsoft Entra ID       Configured External
         Staff/Admin             Candidate Identity
              |                         |
              +------------+------------+
                           |
                           v
                    FastAPI Backend
                           |
                           v
                Backend Authorization
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
         Candidate      Employer     Internal HR
            APIs          APIs        Operations
             |             |             |
             +-------------+-------------+
                           |
                           v
                    Business Services
                           |
                           v
                    Repository Layer
                           |
                           v
                       Azure SQL

Architecture Layers

Layer| Responsibility
Application Users| Candidates, employers, HR personnel, and administrators accessing the application
React 19 / Vite| Frontend application and user interface
Identity Authentication| Authentication through the configured identity providers
Microsoft Entra ID| Identity and authentication services for configured application users
FastAPI Backend| Backend API entry point and request handling
Backend Authorization| Role-based access control and permission enforcement
Candidate APIs| Candidate profile, registration, application, and related operations
Employer APIs| Employer access, organization, dashboard, and recruitment operations
Internal HR Operations| Internal HR and administrative application functionality
Business Services| Application business logic and operational services
Repository Layer| Data access and database interaction
Azure SQL| Relational application data storage

Security Principle

Authentication establishes the identity of the user.

Backend authorization determines which application resources and operations that identity is permitted to access.

The frontend may control the presentation of role-specific functionality, but the backend remains responsible for enforcing authorization on protected API operations.

---

AI-Assisted Policy Capabilities

The backend includes an AI-assisted policy-search and answer-generation flow.

The general process is:

1. Receives a workplace or HR-related question.
2. Retrieves relevant policy content through Azure AI Search.
3. Supplies retrieved policy context to Azure OpenAI.
4. Generates an answer based on the supplied policy content.

These capabilities depend on the relevant service configuration, credentials, permissions, and knowledge sources.

AI-generated responses should be evaluated against the authoritative policy documents and applicable organizational requirements.

Microsoft Foundry agents, Teams channels, and Microsoft 365 experiences configured separately should not be considered integrated with the portal unless their application connections and end-to-end functionality have been independently verified.

---

Repository Structure

The repository is organized into application modules, frontend resources, backend services, tests, CI workflows, and technical documentation.

TBBD-HR-Portal/
│
├── api/                         # FastAPI route modules
│
├── services/                    # Application and authorization services
│
├── models/                      # Application models
│
├── repositories/                # Data-access repositories
│
├── tests/                       # Automated tests
│
├── frontend/                    # React and Vite application
│   ├── package.json
│   ├── package-lock.json
│   └── ...
│
├── documentation/
│   ├── architecture/
│   ├── development/
│   ├── governance/
│   ├── operations/
│   └── roadmap/
│
├── .github/
│   └── workflows/               # GitHub Actions workflows
│
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python application dependencies
├── requirements-dev.txt         # Development/test dependencies
├── Dockerfile                   # Container build definition
├── start.sh                     # Container startup script
├── azure-pipelines.yml          # Azure DevOps CI pipeline
├── SECURITY.md                  # Security policy
├── LICENSE                      # MIT License
└── README.md

The structure above represents the principal repository components. Individual modules and supporting files may evolve during development.

---

Documentation

The repository follows a modular documentation structure to support architecture, development, governance, operations, and future product planning.

Documentation Library

Category| Description
"Architecture" (documentation/architecture/README.md)| Enterprise architecture, Azure design, identity, security, data, integration, and AI architecture
"Development" (documentation/development/README.md)| Development lifecycle, repository standards, CI/CD, branching strategy, and engineering practices
"Governance" (documentation/governance/README.md)| Governance framework, Responsible AI, compliance, risk management, and enterprise standards
"Operations" (documentation/operations/README.md)| Operational procedures, monitoring, maintenance, incident response, and recovery guidance
"Roadmap" (documentation/roadmap/README.md)| Product vision, strategic direction, future capabilities, and release planning

For security-related information, refer to "SECURITY.md" (SECURITY.md).

---

Getting Started

This section explains how to prepare a local development environment.

Prerequisites

Install the following development tools:

- Python 3.11.
- Node.js 20.
- npm.
- Git.
- A code editor such as Visual Studio Code.
- Access to the required Microsoft Entra ID and Azure services for the functionality being tested.

Some application features require additional local configuration and access to external Azure resources.

1. Clone the Repository

git clone https://github.com/Talent-Bridge-BD/TBBD-HR-Portal.git

cd TBBD-HR-Portal

2. Create a Python Virtual Environment

macOS / Linux

python3.11 -m venv .venv

source .venv/bin/activate

Windows PowerShell

py -3.11 -m venv .venv

.\.venv\Scripts\Activate.ps1

3. Install Backend Dependencies

Upgrade pip and install the required application dependencies.

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

python -m pip install -r requirements-dev.txt

4. Install Frontend Dependencies

Navigate to the frontend directory:

cd frontend

Install the dependencies using the committed lockfile:

npm ci

5. Build the Frontend

npm run build

The production build generates the frontend distribution assets.

6. Start the Frontend Development Server

npm run dev

The Vite development server provides the local frontend development environment.

7. Start the Backend

Open a separate terminal session and navigate to the repository root.

Activate the Python virtual environment if necessary.

Start the FastAPI development server:

uvicorn main:app --reload

The backend API is then available through the configured local development environment.

Local Development Notes

- Run the frontend and backend development servers in separate terminal sessions.
- Configure the required environment variables before starting the backend.
- Ensure the required database drivers and dependencies are installed.
- Configure the appropriate identity provider settings for authentication testing.
- Azure-dependent functionality requires access to the relevant Azure resources.
- Local authentication and production authentication may use different configurations.

A successful frontend build or backend startup does not automatically establish connectivity to Azure services or confirm production readiness.

---

Configuration and Security

The application uses identity, database, and external service configuration to support its functionality.

Configuration Principles

- Keep credentials, tokens, connection strings, and API keys outside source control.
- Use approved environment configuration.
- Prefer managed identity where supported.
- Apply least-privilege access to application and cloud resources.
- Maintain separate authorization boundaries for candidates, employers, and internal staff.
- Validate permissions on the backend.
- Protect sensitive candidate and employer information.
- Review dependencies and security alerts regularly.
- Maintain appropriate authentication and authorization controls.
- Follow the repository security policy.

Identity and Access Management

The application uses configured identity providers and backend authorization services.

Authentication and authorization must be treated as separate security responsibilities.

The application should enforce:

- Appropriate identity verification.
- Role-based access restrictions.
- Backend permission validation.
- Organization-level access boundaries where applicable.
- Protection against unauthorized API operations.
- Secure handling of authentication tokens and sensitive information.

Secrets Management

Never commit production secrets or sensitive configuration files to GitHub.

Sensitive values must be supplied through approved environment configuration and Azure security mechanisms.

For additional security guidance, see "SECURITY.md" (SECURITY.md).

---

Continuous Integration and Validation

The repository uses Azure DevOps Pipelines and GitHub Actions for automated validation and repository checks.

Azure DevOps CI Pipeline

The root "azure-pipelines.yml" defines the Azure DevOps Continuous Integration pipeline.

Agent Configuration

Property| Configuration
Agent Pool| "TBBD-Agent-Pool"
Self-hosted Agent| "TBBD-Mac-Agent-01-ARM-native"
Platform| Native macOS ARM64
Python| 3.11 ARM64
Node.js| 20

Pipeline Validation

Pipeline validation includes:

- Native macOS ARM64 environment verification.
- Python 3.11 environment setup.
- Backend dependency installation.
- Frontend dependency installation.
- Frontend production build.
- Frontend distribution asset verification.
- Python source compilation.
- Automated backend test execution.

Pipeline Triggers

The configured pipeline supports:

- Pushes to "main".
- Pull requests targeting "main".

Important: The Azure DevOps pipeline performs Continuous Integration validation only. It does not deploy the application or modify production Azure resources.

GitHub Actions

The repository also contains GitHub Actions workflows for automated repository validation and security checks.

These include:

- Documentation and Markdown validation.
- CodeQL security analysis.
- Infrastructure-related validation.

Infrastructure validation should be understood according to the checks actually implemented in each workflow.

The presence of infrastructure directories or validation workflows does not establish that complete, deployable infrastructure templates are available.

Testing and Quality Assurance

Automated tests support application validation and help identify regressions during development.

Testing should cover:

- Backend API functionality.
- Authentication and authorization.
- Role-specific access restrictions.
- Candidate operations.
- Employer operations.
- Internal HR operations.
- Database interaction.
- Error handling.
- Application integration points.

Test results should be reviewed before approving changes for integration or release.

---

Container Build

The repository includes a multi-stage Dockerfile for building the frontend and packaging the application backend.

Frontend Build Stage

The frontend build stage:

- Uses Node.js 20.
- Installs frontend dependencies with "npm ci".
- Builds the React application using Vite.
- Generates the frontend distribution assets.

Backend Runtime Stage

The backend runtime stage:

- Uses Python 3.11.
- Installs Microsoft ODBC Driver 18 and required system dependencies.
- Installs Python application dependencies.
- Copies backend application modules.
- Copies the built frontend distribution.
- Starts the application through "start.sh".

Container Build

Build the Docker image from the repository root:

docker build -t tbbd-hr-portal .

The resulting image can be used for local container validation and other approved container workflows.

Container image creation and production deployment are separate activities.

Deployment requires its own approved release, configuration, security review, and verification process.

---

Current Project Status

The TBBD HR Portal is under active development.

The following table describes the general implementation status of repository components and capabilities.

Component| Status
React Frontend| Implemented
FastAPI Backend| Implemented
Candidate API Modules| Available
Employer API Modules| Available; ongoing validation
Staff and Administrator API Modules| Available
Authorization Services| Implemented
Repository and Data Access Layer| Implemented
Azure SQL Connectivity| Implemented in application code
Microsoft Identity Integration| Application integration implemented
Docker Build Definition| Available
Automated Backend Tests| Available
Azure DevOps CI Pipeline| Configured
GitHub Actions Workflows| Available
Enterprise Documentation| Maintained
Infrastructure as Code| Requires separate template and deployment verification
External AI and Microsoft 365 Integrations| Require independent integration verification
Production Readiness| Subject to release validation

Project Status Notes

- Implementation status does not necessarily indicate successful production operation.
- Individual application modules may require additional testing and validation.
- Employer dashboard and related functionality remain subject to operational verification.
- External service integrations depend on their respective configurations and permissions.
- Production readiness must be established through formal release validation.

The status information in this README describes repository implementation and configuration, not a guarantee of live production availability.

---

Development Guidelines

Contributions and development activities should follow the repository's established engineering and security practices.

Development Principles

- Follow the existing application architecture.
- Maintain clear separation between frontend and backend responsibilities.
- Keep business logic within appropriate backend services.
- Enforce authorization on protected backend operations.
- Avoid exposing sensitive information through API responses.
- Maintain consistent error handling.
- Write maintainable and reusable code.
- Add or update automated tests when modifying application behavior.
- Update technical documentation when architecture or functionality changes.
- Review changes before merging them into the main branch.

Branching and Integration

Development should follow the repository's established Git branching and pull request practices.

Changes targeting "main" should undergo the required review and automated validation before integration.

Production changes must follow the applicable release approval and deployment procedures.

---

Support

For technical assistance, architecture discussions, documentation updates, security reviews, or platform improvement discussions, use approved Talent Bridge BD internal communication channels.

Support areas include:

- Application development.
- Candidate and employer workflows.
- Recruitment operations.
- Microsoft identity and authorization.
- Azure application services.
- Database connectivity.
- CI validation.
- Security and governance.
- Technical documentation.
- Application maintenance and improvement.

---

License

This project is distributed under the MIT License.

Copyright and licensing information are provided in the ""LICENSE"" (LICENSE) file.

---

<p align="center">
  <strong>Talent Bridge BD (TBBD)</strong>
  <br>
  Connecting Bangladeshi Talent with Global Employment Opportunities.
  <br><br>
  <strong>Secure • Intelligent • Connected • Modern</strong>
  <br><br>
  Microsoft Azure • Microsoft Entra ID • React • FastAPI • Azure SQL
</p>---

<p align="center">
  <strong>Repository:</strong> TBBD-HR-Portal
  <br>
  <strong>Project Status:</strong> Active Development
  <br>
  <strong>Maintained by:</strong> Talent Bridge BD Technology Team
</p>