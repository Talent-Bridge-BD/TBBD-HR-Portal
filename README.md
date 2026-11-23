# TBBD HR Portal

> The Talent Bridge BD Human Resources platform — a web application for recruitment, candidate and employer access, and internal HR operations, built with React, FastAPI, and Microsoft Azure services.

![Frontend](https://img.shields.io/badge/Frontend-React%2019-61DAFB)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![Node](https://img.shields.io/badge/Node.js-20-339933)
![Identity](https://img.shields.io/badge/Identity-Microsoft%20Entra%20ID-5C2D91)
![Cloud](https://img.shields.io/badge/Cloud-Microsoft%20Azure-0078D4)
![CI](https://img.shields.io/badge/CI-Azure%20DevOps%20%7C%20GitHub%20Actions-2088FF)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Welcome

Welcome to the **TBBD HR Portal** repository.

The TBBD HR Portal is the Human Resources application developed for **Talent Bridge BD (TBBD)**.

The repository contains the application source code, backend API services, frontend application, data-access components, automated validation workflows, and technical documentation.

The platform is designed to support recruitment and HR operations through role-aware access for candidates, employers, and internal staff.

---

## Table of Contents

- [Repository Information](#repository-information)
- [Overview](#overview)
- [Vision](#vision)
- [Objectives](#objectives)
- [Key Capabilities](#key-capabilities)
- [Technology Stack](#technology-stack)
- [Application Architecture](#application-architecture)
- [AI-Assisted Policy Capabilities](#ai-assisted-policy-capabilities)
- [Repository Structure](#repository-structure)
- [Documentation](#documentation)
- [Getting Started](#getting-started)
- [Configuration and Security](#configuration-and-security)
- [Continuous Integration and Validation](#continuous-integration-and-validation)
- [Container Build](#container-build)
- [Current Project Status](#current-project-status)
- [Support](#support)
- [License](#license)

---

## Repository Information

| Property | Value |
|---|---|
| Project | TBBD HR Portal |
| Organization | Talent Bridge BD (TBBD) |
| Repository | TBBD-HR-Portal |
| Version | v1.0.0 |
| Status | Active Development |
| Frontend | React 19 / Vite |
| Backend | Python 3.11 / FastAPI |
| Cloud Platform | Microsoft Azure |
| Identity Platform | Microsoft Entra ID |
| Source Control | GitHub |
| Maintained By | Talent Bridge BD Technology Team |
| License | MIT |

---

## Overview

The TBBD HR Portal is designed to modernize recruitment and Human Resources operations through a secure, role-aware web application.

The platform combines:

- Modern React-based user experiences
- FastAPI backend services
- Microsoft Entra ID authentication
- Backend role-based authorization
- Employer and candidate management capabilities
- Recruitment and application workflows
- Azure SQL database connectivity
- Azure service integrations
- Automated testing and CI validation

This repository serves as the source for application code, technical implementation, automated validation, and supporting documentation.

---

## Vision

To build a secure, intelligent, scalable, and modern Human Resources platform that connects Bangladeshi talent with global employment opportunities while supporting employers and internal HR operations.

---

## Objectives

The TBBD HR Portal aims to:

- Modernize Human Resources operations
- Improve candidate access and profile management
- Simplify employer access and recruitment workflows
- Support secure workplace access
- Strengthen identity and authorization controls
- Improve recruitment and hiring processes
- Support document and application management
- Enable AI-assisted workplace capabilities
- Maintain enterprise security and governance
- Promote maintainable software development
- Improve automated testing and validation

---

## Key Capabilities

### Candidate Portal

Designed to support candidate-facing operations, including:

- Candidate registration and access
- Candidate profile management
- Personal and professional information
- Document management
- Job application workflows
- Application status and recruitment processing

### Employer Portal

Designed to support employer-facing operations, including:

- Employer access
- Organization-related operations
- Employer dashboard
- Job and vacancy management
- Recruitment workflows
- Candidate application management

### Staff and Administrator Portal

Supports internal HR and administrative operations, including:

- Staff and administrator access
- Role-based application permissions
- Organization management
- Candidate approval workflows
- Recruitment administration
- Internal HR operational capabilities

### Recruitment and Processing

The backend contains API modules supporting areas such as:

- Job management
- Job requests
- Applications
- Interviews
- Trade tests
- Candidate screening
- Medical examinations
- Visa processing
- Ticketing and onboarding
- Recruitment pipeline operations

The presence of an API module does not, by itself, establish that every workflow is fully deployed or operational in production.

---

## Technology Stack

| Area | Technology |
|---|---|
| Frontend | React 19 |
| Frontend Build Tool | Vite |
| Browser Authentication | Microsoft Authentication Library (MSAL Browser) |
| Backend | Python 3.11 |
| API Framework | FastAPI |
| API Server | Uvicorn |
| Identity Platform | Microsoft Entra ID |
| Authorization | Application-level role-based access control |
| Database | Azure SQL / SQL Server |
| Database Connectivity | pyodbc |
| Azure Identity | Azure Identity SDK |
| File Storage | Azure Storage SDK |
| Artificial Intelligence | Azure OpenAI SDK and Azure AI Search integration |
| Email Services | Azure Communication Services Email SDK |
| PDF Generation | ReportLab |
| Containerization | Docker |
| Frontend Runtime and Build | Node.js 20 / npm |
| Source Control | GitHub |
| CI Validation | Azure DevOps Pipelines / GitHub Actions |

---

## Application Architecture

The TBBD HR Portal follows a layered application architecture that separates user authentication, backend authorization, role-specific API operations, and data access.

```text
                    Application Users
                         |
                         v
                 React 19 / Vite
                         |
                         v
              Microsoft Entra ID
                 Authentication
                         |
                         v
                  FastAPI Backend
                         |
                         v
              Authorization Services
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
         Candidate    Employer    Staff/Admin
           APIs        APIs          APIs
             |           |           |
             +-----------+-----------+
                         |
                         v
                 Repository Layer
                         |
                         v
                     Azure SQL
```

### Architecture Layers

| Layer | Responsibility |
|---|---|
| Application Users | Candidates, employers, HR personnel, and administrators accessing the portal |
| React 19 / Vite | Frontend application and user interface |
| Microsoft Entra ID | User authentication and identity management |
| FastAPI Backend | Backend API entry point and request handling |
| Authorization Services | Role-based access control and permission enforcement |
| Candidate APIs | Candidate profile, registration, application, and related operations |
| Employer APIs | Employer access, organization, dashboard, and recruitment operations |
| Staff/Admin APIs | Internal HR operations, administration, and management operations |
| Repository Layer | Data access and database interaction |
| Azure SQL | Relational application data storage |

**Security principle:** Authentication establishes the user's identity; backend authorization services determine which application resources and operations that identity is permitted to access.

---

## AI-Assisted Policy Capabilities

The backend includes an AI-assisted policy-search and answer-generation flow.

The general process is:

1. Receives a workplace or HR-related question.
2. Retrieves relevant policy content through Azure AI Search.
3. Supplies retrieved policy context to Azure OpenAI.
4. Generates an answer based on the supplied policy content.

These capabilities depend on the relevant service configuration, credentials, and knowledge sources.

Microsoft Foundry agents, Teams channels, and Microsoft 365 experiences configured separately should not be considered integrated with the portal unless their application connection has been independently verified.

---

## Repository Structure

```text
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
```

---

## Documentation

The repository follows a modular documentation structure to support architecture, development, governance, operations, and future product planning.

### Documentation Library

| Category | Description |
|---|---|
| [Architecture](documentation/architecture/README.md) | Enterprise architecture, Azure design, identity, security, data, integration, and AI architecture |
| [Development](documentation/development/README.md) | Development lifecycle, repository standards, CI/CD, branching strategy, and engineering practices |
| [Governance](documentation/governance/README.md) | Governance framework, Responsible AI, compliance, risk management, and enterprise standards |
| [Operations](documentation/operations/README.md) | Operational procedures, monitoring, maintenance, incident response, and recovery guidance |
| [Roadmap](documentation/roadmap/README.md) | Product vision, strategic direction, future capabilities, and release planning |

---

## Getting Started

### Prerequisites

Install the following development tools:

- Python 3.11
- Node.js 20
- npm
- Git
- Access to required Microsoft Entra ID and Azure services for the functionality being tested

### 1. Clone the Repository

```bash
git clone https://github.com/Talent-Bridge-BD/TBBD-HR-Portal.git

cd TBBD-HR-Portal
```

### 2. Create a Python Virtual Environment

macOS / Linux:

```bash
python3.11 -m venv .venv

source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv

.\.venv\Scripts\Activate.ps1
```

### 3. Install Backend Dependencies

```bash
python -m pip install --upgrade pip

python -m pip install -r requirements.txt

python -m pip install -r requirements-dev.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend

npm ci
```

### 5. Build the Frontend

```bash
npm run build
```

### 6. Start the Frontend Development Server

```bash
npm run dev
```

### 7. Run the Backend

Return to the repository root and configure the required environment settings.

```bash
cd ..

uvicorn main:app --reload
```

The application requires appropriate identity, database, and service configuration. A successful local build does not automatically establish connectivity to Azure or production resources.

---

## Configuration and Security

The application uses identity, database, and external service configuration to support its functionality.

Security practices include:

- Keep credentials, tokens, connection strings, and API keys outside source control.
- Use approved environment configuration.
- Prefer managed identity where supported.
- Apply least-privilege access to application and cloud resources.
- Maintain separate authorization boundaries for candidates, employers, and internal staff.
- Validate permissions on the backend.
- Protect sensitive candidate and employer information.
- Review dependencies and security alerts regularly.
- Follow the repository security policy.

Never commit production secrets or sensitive configuration files to GitHub.

For security guidance, see [SECURITY.md](SECURITY.md).

---

## Continuous Integration and Validation

The repository uses Azure DevOps Pipelines and GitHub Actions for automated validation.

### Azure DevOps CI Pipeline

The root `azure-pipelines.yml` defines the Azure DevOps Continuous Integration pipeline.

**Agent configuration**

- Agent pool: `TBBD-Agent-Pool`
- Self-hosted agent: `TBBD-Mac-Agent-01-ARM-native`
- Platform: Native macOS ARM64
- Python: 3.11 ARM64
- Node.js: 20

**Pipeline validation includes:**

- Native macOS ARM64 environment verification
- Python 3.11 environment setup
- Backend dependency installation
- Frontend dependency installation
- Frontend production build
- Frontend distribution asset verification
- Python source compilation
- Automated backend test execution

**Pipeline triggers**

- Pushes to `main`
- Pull requests targeting `main`

**Important:** This pipeline performs CI validation only. It does not deploy the application or modify production resources.

### GitHub Actions

The repository also contains GitHub Actions workflows for automated repository validation and security checks.

These include:

- Documentation and Markdown validation
- CodeQL security analysis
- Infrastructure-related validation

Infrastructure validation should be understood according to the checks actually implemented in the workflow. The presence of infrastructure directories does not establish that complete, deployable infrastructure templates are available.

---

## Container Build

The repository includes a multi-stage Dockerfile.

### Frontend Build Stage

- Uses Node.js 20.
- Installs frontend dependencies with `npm ci`.
- Builds the React application using Vite.

### Backend Runtime Stage

- Uses Python 3.11.
- Installs Microsoft ODBC Driver 18 and required system dependencies.
- Installs Python application dependencies.
- Copies backend application modules.
- Copies the built frontend distribution.
- Starts the application through `start.sh`.

Container build and production deployment are separate activities. Deployment requires its own approved release and verification process.

---

## Current Project Status

The TBBD HR Portal is under active development.

| Component | Status |
|---|---|
| React Frontend | Implemented |
| FastAPI Backend | Implemented |
| Candidate API Modules | Available |
| Employer API Modules | Available |
| Staff and Administrator API Modules | Available |
| Authorization Services | Implemented |
| Repository and Data Access Layer | Implemented |
| Azure SQL Connectivity | Implemented in application code |
| Microsoft Entra ID Authentication | Application integration implemented |
| Docker Build Definition | Available |
| Automated Backend Tests | Available |
| Azure DevOps CI Pipeline | Configured |
| GitHub Actions Workflows | Available |
| Enterprise Documentation | Maintained |
| Infrastructure as Code | Requires separate template and deployment verification |
| External AI and Microsoft 365 Integrations | Require independent integration verification |
| Production Readiness | Subject to release validation |

Status describes repository implementation and configuration, not a guarantee of live production availability.

---

## Support

For technical assistance, architecture discussions, documentation updates, security reviews, or platform improvement discussions, use approved Talent Bridge BD internal communication channels.

Support areas include:

- Application development
- Candidate and employer workflows
- Recruitment operations
- Microsoft Entra ID and authorization
- Azure application services
- Database connectivity
- CI validation
- Security and governance
- Technical documentation

---

## License

This project is distributed under the **MIT License**.

Copyright and licensing information are provided in the [`LICENSE`](LICENSE) file.

---

<div align="center">

## Talent Bridge BD (TBBD)

### Connecting Bangladeshi Talent with Global Employment Opportunities.

**Secure • Intelligent • Connected • Modern**

Microsoft Azure • Microsoft Entra ID • React • FastAPI • Azure SQL

---

Repository: `TBBD-HR-Portal`

Version: `v1.0.0`

Status: `Active Development`

Maintained by: Talent Bridge BD Technology Team

</div>
