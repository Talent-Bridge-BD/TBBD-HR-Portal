# TBBD HR Portal

> The Talent Bridge BD Human Resources platform — a unified digital
> workplace for recruitment, candidate services, employer access, and
> internal HR operations.

![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Build-Vite-646CFF?logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![Microsoft Azure](https://img.shields.io/badge/Cloud-Microsoft%20Azure-0078D4?logo=microsoftazure&logoColor=white)
![Microsoft Entra ID](https://img.shields.io/badge/Identity-Microsoft%20Entra%20ID-5E5E5E?logo=microsoft&logoColor=white)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Project-Active%20Development-orange)

---

## Table of Contents

- [Overview](#overview)
- [About Talent Bridge BD](#about-talent-bridge-bd)
- [Platform Architecture](#platform-architecture)
- [Core Portals and User Access](#core-portals-and-user-access)
- [Key Capabilities](#key-capabilities)
- [Technology Stack](#technology-stack)
- [Microsoft Azure Infrastructure](#microsoft-azure-infrastructure)
- [Authentication and Authorization](#authentication-and-authorization)
- [Application Architecture](#application-architecture)
- [Repository Structure](#repository-structure)
- [Local Development Setup](#local-development-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing and Quality Assurance](#testing-and-quality-assurance)
- [CI and Development Workflows](#ci-and-development-workflows)
- [Security](#security)
- [Deployment and Operations](#deployment-and-operations)
- [Project Status](#project-status)
- [Future Development](#future-development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **TBBD HR Portal** is the centralized human resources and workforce
management platform developed for **Talent Bridge BD (TBBD)**.

The platform is designed to connect Bangladeshi talent with global
employment opportunities while supporting employers and internal HR
teams through a unified digital environment.

It brings together candidate-facing services, employer-facing
recruitment workflows, and internal HR operations within a single
application.

The platform follows a modern web application architecture using React,
FastAPI, Microsoft Azure services, and Microsoft identity technologies.

### Main Objectives

- Provide a centralized digital platform for candidates and employers.
- Support recruitment and workforce management workflows.
- Facilitate employer access requests and recruitment requirements.
- Manage candidate information and recruitment-related activities.
- Support internal HR operations and administrative management.
- Apply role-based access controls across application areas.
- Provide secure authentication and API access.
- Integrate with selected Microsoft Azure services.

The application is actively under development, with ongoing improvements
to functionality, authorization, integrations, and operational
reliability.

---

## About Talent Bridge BD

**Talent Bridge BD (TBBD)** is a recruitment and workforce solutions
initiative of **Loyal Trade Management Ltd**.

The initiative focuses on connecting skilled Bangladeshi professionals
and workers with employment opportunities in international markets.

The TBBD HR Portal provides the digital foundation for supporting this
mission through recruitment services, employer engagement, candidate
management, and internal HR operations.

### Platform Relationship

- **Loyal Trade Management Ltd:** Parent organization.
- **Talent Bridge BD:** Recruitment and workforce solutions initiative.
- **TBBD HR Portal:** Centralized digital platform supporting the initiative.
- **TBBD Workplace Hub:** Unified access point for the platform's user journeys.

---

## Platform Architecture

The TBBD HR Portal follows a centralized application model.

Instead of maintaining separate applications for each user group, the
platform provides different access areas within one application.

```text
                    Talent Bridge BD
                           |
                           |
                   TBBD Workplace Hub
                           |
                           |
                    TBBD HR Portal
                           |
          +----------------+----------------+
          |                |                |
          |                |                |
      Candidate         Employer       Staff / Admin
        Portal           Portal            Portal
          |                |                |
          |                |                |
      Candidate         Employer        HR Operations
       Services         Services       Administration
          |                |                |
          +----------------+----------------+
                           |
                           |
                    FastAPI Backend
                           |
          +----------------+----------------+
          |                |                |
       Database       Azure Services     Identity
          |                |                |
       Azure SQL      AI / Storage       Entra ID
                                         External
                                         Identity
```

The architecture separates the frontend, backend APIs, data access,
identity management, and supporting cloud services.

---

## Core Portals and User Access

The platform provides three primary user access areas.

### 1. Candidate Portal

The Candidate Portal supports individuals seeking employment
opportunities through Talent Bridge BD.

Key functionality includes:

- Candidate registration and sign-in.
- Candidate profile management.
- Personal and professional information.
- Skills, qualifications, and experience management.
- Passport and relevant document information.
- Recruitment-related application activities.
- Candidate profile completion and review.
- Access to relevant recruitment services.

Candidate access and recruitment-related permissions are subject to the
platform's configured identity and authorization rules.

### 2. Employer Portal

The Employer Portal is designed for organizations seeking recruitment
and workforce solutions through Talent Bridge BD.

Key functionality includes:

- Employer access requests.
- Organization and representative information.
- Employer account access following approval.
- Recruitment and workforce requirement submission.
- Talent request management.
- Employer-related information and workflows.
- Access to relevant recruitment services.

Employer access is based on an approval and invitation process rather
than unrestricted public registration.

Employer functionality is under active development and requires
continued workflow and dashboard validation.

### 3. Staff and Administrator Portal

The Staff and Administrator Portal supports internal operations and
administrative responsibilities.

It provides the internal working environment for authorized personnel.

Key areas include:

- HR operations.
- Candidate administration.
- Employer administration.
- Recruitment management.
- User and role management.
- Organization-related administration.
- Operational dashboards.
- Administrative functions.
- Internal platform management.

Access to these functions is controlled by authentication and backend
authorization.

**Note:** HR Operations is part of the Staff and Administrator Portal.
The platform does not maintain a separate Employee Portal.

---

## Key Capabilities

### Candidate Management

- Candidate registration and authentication.
- Candidate profile information.
- Profile completion tracking.
- Professional qualifications and experience.
- Candidate document information.
- Recruitment-related candidate management.

### Employer Management

- Employer access request submission.
- Employer organization information.
- Administrative review of access requests.
- Employer invitation and account access.
- Recruitment requirement management.

### Recruitment Management

The platform is designed to support recruitment activities and related
workforce workflows.

The intended recruitment lifecycle includes:

1. Employer workforce requirement submission.
2. Administrative review of employer requirements.
3. Recruitment request processing.
4. Candidate sourcing and management.
5. Candidate screening and selection.
6. Interview and assessment coordination.
7. Medical and documentation processes.
8. Visa and deployment-related activities.
9. Onboarding and deployment tracking.

The availability of individual workflow stages depends on the current
implementation and configuration.

### Internal HR Operations

- Internal HR administration.
- Candidate and employer oversight.
- Recruitment operations.
- User and access administration.
- Operational reporting and dashboards.

### Secure Application Access

- Microsoft Entra ID authentication for internal users.
- Configured external identity authentication for candidate access.
- Backend role-based authorization.
- Protected application routes and APIs.
- Secure access to application resources.

---

## Technology Stack

The project uses the following technologies and development tools.

### Frontend

| Technology | Purpose |
|---|---|
| React 19 | User interface development |
| Vite | Frontend development and build tooling |
| JavaScript | Application logic |
| CSS | Styling and responsive layouts |
| MSAL Browser | Microsoft identity authentication in the browser |

### Backend

| Technology | Purpose |
|---|---|
| Python 3.11 | Backend programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI application server |
| Pydantic | Data validation and settings |
| pyodbc | SQL Server database connectivity |
| ReportLab | PDF document generation |

### Microsoft Azure and Cloud SDKs

| Technology | Purpose |
|---|---|
| Microsoft Azure App Service | Application hosting |
| Microsoft Entra ID | Identity and access management |
| Azure SQL | Relational database services |
| Azure Identity SDK | Azure authentication and credentials |
| Azure Storage SDK | Azure Storage access |
| Azure AI Search | Search capabilities |
| Azure OpenAI | AI capabilities |
| Azure Communication Services Email SDK | Email communication capabilities |
| Azure Front Door Premium | Application entry point and edge delivery |

The availability and use of individual cloud integrations depend on
their configuration and implementation within the application.

### Development and Infrastructure

| Technology | Purpose |
|---|---|
| Docker | Containerization |
| Node.js 20 | Frontend runtime and tooling |
| npm | JavaScript package management |
| Git | Version control |
| GitHub | Source code management |
| Azure DevOps | Build and pipeline management |
| GitHub Actions | Repository automation and validation |

---

## Microsoft Azure Infrastructure

The application uses Microsoft Azure as its cloud hosting and
infrastructure platform.

The configured environment includes the following services and
components.

| Azure Service / Component | Purpose |
|---|---|
| Azure App Service | Hosts the TBBD HR Portal application |
| Azure SQL | Application database |
| Microsoft Entra ID | Internal identity authentication |
| Entra External ID configuration | Candidate identity authentication |
| Azure Front Door Premium | External application entry point |
| Azure Virtual Network | Network isolation and integration |
| Private Endpoints | Private connectivity to supported Azure resources |
| Private DNS | Private resource name resolution |
| Azure AI Search | Search service |
| Azure OpenAI | AI service |
| Azure Storage | Application storage capabilities |
| Azure Communication Services | Email communication capabilities |

### Hosting

The main application is hosted through Azure App Service.

The platform uses a unified application deployment model rather than
separate App Services for each portal.

### Network Architecture

The Azure environment includes network components designed to support
secure connectivity between application and supporting services.

These include:

- Azure Virtual Network.
- App Service VNet integration.
- Private Endpoints.
- Private DNS.
- Supporting network infrastructure.

### Application Entry Point

Azure Front Door Premium is configured as part of the platform's
external application delivery architecture.

Its configuration, routing, origin connectivity, and security policies
should be monitored as part of ongoing operational validation.

---

## Authentication and Authorization

Security is an important part of the TBBD HR Portal architecture.

The platform uses Microsoft identity technologies and backend
authorization controls to manage access.

### Authentication

The application supports different authentication paths according to
user type.

| User Type | Authentication |
|---|---|
| Candidates | Configured external identity provider |
| Employers | Approved employer access and configured sign-in |
| Staff | Microsoft Entra ID |
| Administrators | Microsoft Entra ID and administrative authorization |

### Authorization

The backend applies role-based access control (RBAC) to protect
application functionality and resources.

Authorization is enforced through backend permissions rather than
relying exclusively on frontend navigation or visibility.

The application is designed to ensure that:

- Users can access only authorized application areas.
- Administrative functionality is restricted to authorized roles.
- Employer access is separated from internal administrative access.
- Candidate access is restricted to permitted candidate functionality.
- API endpoints apply appropriate authorization checks.

### Identity and Access Management

The identity architecture uses Microsoft Entra technologies for internal
users and the configured external identity provider for candidate
authentication.

Identity configuration, role assignments, group memberships, and
cross-tenant access must be verified against the actual deployment
environment.

---

## Application Architecture

The application uses a frontend and backend architecture.

### Frontend Architecture

The frontend is developed with React and Vite.

Its responsibilities include:

- User interface rendering.
- Portal navigation.
- User interactions.
- Form handling.
- Authentication integration.
- API communication.
- Role-aware application experiences.

### Backend Architecture

The backend is developed with Python and FastAPI.

Its responsibilities include:

- REST API endpoints.
- Business logic.
- Authentication and authorization enforcement.
- Database operations.
- Data validation.
- Recruitment and HR workflows.
- Integration with supporting Azure services.

### Database Architecture

Azure SQL is used for relational application data.

The backend accesses SQL Server-compatible database services through
`pyodbc`.

Database operations should be managed through the application's
established data access and repository patterns.

### API Integration

The frontend communicates with backend services through HTTP APIs.

The backend is responsible for validating requests, enforcing
permissions, processing business logic, and returning appropriate
responses.

---

## Repository Structure

The repository contains the frontend, backend, application services,
tests, configuration, and development automation.

A representative structure is shown below. Actual directories and
filenames should follow the current repository.

```text
TBBD-HR-Portal/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── assets/
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
│
├── api/
│
├── services/
│
├── models/
│
├── repositories/
│
├── tests/
│
├── docs/
│
├── .github/
│   └── workflows/
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── start.sh
├── azure-pipelines.yml
├── SECURITY.md
├── LICENSE
└── README.md
```

The exact repository structure may evolve as application modules and
services are developed.

---

## Local Development Setup

The following instructions describe the general local development
environment.

### Prerequisites

Install the required development tools:

- Git.
- Python 3.11.
- Node.js 20.
- npm.
- Docker Desktop (if using container-based development).
- Access to the required development database and Azure resources.

### Clone the Repository

```bash
git clone https://github.com/Talent-Bridge-BD/TBBD-HR-Portal.git

cd TBBD-HR-Portal
```

### Frontend Dependencies

```bash
cd frontend

npm install
```

### Backend Dependencies

From the repository root:

```bash
python3.11 -m venv .venv
```

Activate the virtual environment.

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

If a separate development requirements file is maintained, install it
according to the project's development instructions.

---

## Configuration

The application requires environment-specific configuration for local
development and deployment.

Configuration may include:

- Database connection settings.
- Authentication settings.
- Microsoft Entra application configuration.
- External identity provider configuration.
- Azure service endpoints.
- Azure Storage configuration.
- Azure AI Search configuration.
- Azure OpenAI configuration.
- Email service configuration.
- Application environment settings.

Use the project's existing environment configuration template and
deployment documentation to identify the exact variable names.

### Security Requirements

- Do not commit secrets or credentials.
- Do not publish database connection strings.
- Do not store client secrets in frontend code.
- Do not expose access tokens in logs.
- Use secure configuration mechanisms for deployed environments.
- Keep local environment files out of source control.

For Azure-hosted environments, use the configured application settings
and appropriate identity-based access wherever supported.

---

## Running the Application

### Start the Backend

From the repository root, with the Python virtual environment activated:

```bash
uvicorn main:app --reload
```

The backend development server will normally be available at:

```text
http://127.0.0.1:8000
```

Use the application's actual configured startup module and command if
they differ.

### Start the Frontend

Open another terminal:

```bash
cd frontend

npm run dev
```

Vite will display the local frontend address in the terminal.

Open that address in your browser.

### Important Local Development Note

Some authentication and Azure-dependent functionality may require access
to configured cloud resources and identity providers.

Local Docker or development environments may not provide the same
authentication and network access as the deployed Azure environment.

---

## API Documentation

FastAPI provides interactive API documentation.

When the backend is running and the documentation endpoints are enabled,
access:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

These interfaces can be used to inspect available API endpoints, request
schemas, and response models.

API access remains subject to the application's authentication and
authorization requirements.

---

## Testing and Quality Assurance

Testing and validation are important parts of the TBBD HR Portal
development process.

The project uses automated validation and testing to help identify
application defects and prevent regressions.

Areas requiring validation include:

- Backend API functionality.
- Frontend build validation.
- Authentication flows.
- Role-based authorization.
- Candidate access and profile workflows.
- Employer access request workflows.
- Staff and administrator functionality.
- Database connectivity.
- Azure service connectivity.
- Application configuration.
- Security and dependency checks.

### Suggested Local Validation

Frontend production build:

```bash
cd frontend

npm run build
```

Backend tests:

```bash
pytest
```

The actual test commands and available test suites should follow the
repository's current configuration.

A successful build or automated test run does not, by itself, establish
that every live application workflow is operational.

---

## CI and Development Workflows

The repository uses GitHub and Azure DevOps to support source code
management and automated development validation.

### Azure DevOps Pipelines

The repository includes:

```text
azure-pipelines.yml
```

Azure DevOps Pipelines are used for automated build and validation
activities.

The configured pipeline environment includes the TBBD self-hosted agent
infrastructure.

Pipeline execution and successful validation should be monitored through
the Azure DevOps project.

### GitHub Actions

GitHub Actions supports repository automation and validation workflows.

Configured workflow areas include:

- Documentation and Markdown validation.
- CodeQL security analysis.
- Infrastructure-related validation.

The exact checks performed depend on the enabled workflow definitions
in:

```text
.github/workflows/
```

### Development Workflow

The general development process is:

1. Review the current repository and project status.
2. Create or select the appropriate working branch.
3. Implement changes.
4. Run relevant local tests and build checks.
5. Review code changes.
6. Submit changes through the appropriate pull request process.
7. Review automated pipeline results.
8. Merge only after the required reviews and checks are complete.

CI validation should not be confused with automatic production
deployment.

---

## Security

The project is designed with security controls appropriate for a
cloud-hosted HR and recruitment application.

Security considerations include:

- Microsoft identity authentication.
- Backend role-based authorization.
- Protected API endpoints.
- Secure database connectivity.
- Private networking for supported Azure resources.
- Secret and credential protection.
- Dependency and code security checks.
- Controlled employer access.
- Administrative access restrictions.

### Security Best Practices

Contributors should:

- Never commit passwords, tokens, certificates, or client secrets.
- Never bypass authorization checks to make a workflow appear functional.
- Validate permissions on the backend.
- Avoid exposing sensitive candidate or employer information.
- Use parameterized database queries.
- Review changes affecting authentication and authorization carefully.
- Follow the repository's security guidance.

For security-related concerns, refer to:

```text
SECURITY.md
```

---

## Deployment and Operations

The TBBD HR Portal is designed to operate within Microsoft Azure.

The configured hosting architecture includes Azure App Service and
supporting Azure infrastructure.

Operational responsibilities include:

- Application availability monitoring.
- Database connectivity monitoring.
- Authentication and authorization validation.
- Frontend and backend error monitoring.
- Azure resource health checks.
- Front Door routing and origin validation.
- Network and private endpoint validation.
- Application configuration management.
- Backup and recovery planning.
- Security and dependency reviews.

Production readiness should be assessed through end-to-end application
testing, security verification, infrastructure validation, and
operational acceptance.

A successful deployment or pipeline execution alone does not establish
production readiness.

---

## Project Status

Project Status: Active Development

The TBBD HR Portal is under active development and continuous
improvement.

| Area | Current Status |
|---|---|
| Core application architecture | Established |
| React frontend | Implemented |
| FastAPI backend | Implemented |
| Azure App Service hosting | Configured |
| Azure SQL connectivity | Configured; operational validation required |
| Internal Microsoft Entra authentication | Configured |
| Candidate external identity authentication | Configured |
| Backend role-based authorization | Implemented; regression validation ongoing |
| Candidate Portal | Implemented; workflow validation ongoing |
| Employer Portal | Under active development and validation |
| Employer dashboard | Requires continued validation |
| Staff and Administrator Portal | Implemented; feature validation ongoing |
| HR Operations | Part of Staff and Administrator Portal |
| Azure infrastructure | Configured; operational review ongoing |
| Azure DevOps Pipelines | Configured |
| GitHub Actions | Configured |
| Production acceptance | Not yet established |

The status of individual components may change as development, testing,
and deployment activities progress.

---

## Future Development

Planned development and improvement areas include:

- Completing and validating employer workflows.
- Improving employer dashboard reliability.
- Completing candidate workflow regression testing.
- Strengthening internal HR operational capabilities.
- Improving recruitment workflow management.
- Enhancing reporting and dashboard functionality.
- Expanding document and application management.
- Improving automated testing coverage.
- Continuing security and authorization reviews.
- Improving Azure monitoring and operational resilience.
- Validating and expanding integrations where required.

Future integrations will be documented as implemented only after their
actual configuration and application usage have been verified.

---

## Contributing

Contributions should follow the repository's development and review
procedures.

Before submitting changes:

1. Review the existing application architecture.
2. Understand the relevant authentication and authorization requirements.
3. Follow the established coding conventions.
4. Test affected functionality.
5. Run the relevant build and validation checks.
6. Review changes for security and configuration issues.
7. Submit a pull request with a clear description of the changes.

Changes affecting authentication, authorization, database access, or
security-sensitive functionality should receive particular attention
during review.

---

## License

Refer to the repository's `LICENSE` file for applicable licensing terms.

---

## Maintained By

**Talent Bridge BD (TBBD)**  
A recruitment and workforce solutions initiative of Loyal Trade
Management Ltd.

**Platform:** TBBD HR Portal  
**Architecture:** React, FastAPI, and Microsoft Azure  
**Project Status:** Active Development

---

*Connecting Bangladeshi Talent with Global Employment Opportunities.*
