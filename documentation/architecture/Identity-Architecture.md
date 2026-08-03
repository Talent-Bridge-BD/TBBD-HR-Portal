# Identity Architecture

> Identity architecture for the **TBBD HR Portal**, describing authentication, authorization, Microsoft Entra ID integration, identity governance, privileged access, and secure access to enterprise resources.

---

# Document Information

| Property | Value |
|----------|-------|
| Repository | TBBD-HR-Portal |
| Document | Identity Architecture |
| Version | 1.0.0 |
| Owner | Talent Bridge BD Technology Team |
| Classification | Internal |
| Last Updated | August 2026 |
| Review Cycle | Quarterly |

---

# Overview

The TBBD HR Portal uses **Microsoft Entra ID** as its centralized identity provider, delivering secure authentication, authorization, identity governance, and access management across Microsoft Azure, Microsoft 365, and integrated enterprise applications.

The identity architecture follows Microsoft's **Zero Trust** principles, ensuring every identity is authenticated, authorized, and continuously evaluated before access is granted.

---

# Identity Principles

The identity architecture is designed around the following principles:

- Identity-first security
- Zero Trust access
- Least privilege
- Strong authentication
- Continuous verification
- Secure application identities
- Centralized identity management
- Automated lifecycle management
- Enterprise governance
- Compliance by design

---

# Identity Components

| Component | Purpose |
|----------|---------|
| Microsoft Entra ID | Enterprise identity platform |
| Single Sign-On (SSO) | Unified authentication |
| Multi-Factor Authentication (MFA) | Strong user authentication |
| Conditional Access | Risk-based access control |
| Role-Based Access Control (RBAC) | Authorization management |
| Privileged Identity Management (PIM) | Just-in-time privileged access |
| Identity Governance | Access lifecycle management |
| Managed Identities | Secure Azure service authentication |
| Service Principals | Application identities |
| Microsoft Graph API | Identity and directory integration |

---

# Identity Architecture

```text
Users
│
├── Employees
├── HR Administrators
├── Recruiters
├── Managers
└── External Users
        │
        ▼
Microsoft Entra ID
Authentication
Authorization
Identity Governance
Conditional Access
        │
        ▼
TBBD HR Portal
        │
 ┌──────────────┬───────────────┐
 │              │               │
 ▼              ▼               ▼
Microsoft 365   Azure          Azure AI
Teams           App Service    Foundry
SharePoint      Functions      OpenAI
Exchange        Storage        AI Search
Graph API       Key Vault
```

---

# Authentication

Authentication is centralized through Microsoft Entra ID.

Supported capabilities include:

- Single Sign-On (SSO)
- Multi-Factor Authentication (MFA)
- Passwordless authentication
- FIDO2 security keys
- Microsoft Authenticator
- OAuth 2.0
- OpenID Connect
- SAML 2.0 (where required)

---

# Authorization

Authorization is implemented using Role-Based Access Control (RBAC).

Typical roles include:

- Employee
- Recruiter
- HR Officer
- HR Manager
- Department Manager
- IT Administrator
- Security Administrator
- Global Administrator

Access permissions follow the **Principle of Least Privilege**.

---

# Conditional Access

Conditional Access policies help protect identities by evaluating:

- User identity
- Device compliance
- Location
- Risk level
- Application
- Session controls

Common policies include:

- Require MFA
- Block legacy authentication
- Restrict high-risk sign-ins
- Require compliant devices
- Restrict administrative access

---

# Identity Governance

Identity governance supports secure lifecycle management.

Capabilities include:

- Joiner, Mover, Leaver (JML) processes
- Access Reviews
- Entitlement Management
- Group lifecycle management
- Role assignments
- Automated provisioning
- Automated deprovisioning

---

# Privileged Identity Management (PIM)

Administrative access is protected through Microsoft Entra PIM.

Key capabilities:

- Just-In-Time (JIT) access
- Approval workflows
- Time-limited role activation
- MFA for privileged roles
- Audit history
- Access reviews

---

# Managed Identities

Azure Managed Identities are used for secure communication between Azure services.

Benefits include:

- No stored credentials
- Automatic credential rotation
- Secure Key Vault access
- Azure resource authentication

---

# Application Identity

Enterprise applications use:

- App Registrations
- Service Principals
- OAuth 2.0
- Microsoft Graph permissions
- Managed identities where supported

---

# Microsoft Graph Integration

Microsoft Graph enables secure access to Microsoft 365 resources.

Supported integrations include:

- Users
- Groups
- Teams
- SharePoint
- Calendars
- Mail
- Files
- Organizational data

---

# Security Best Practices

Identity security includes:

- MFA enforcement
- Passwordless authentication
- Least privilege
- Conditional Access
- Continuous monitoring
- Privileged access management
- Secure application identities
- Identity Protection
- Audit logging

---

# Monitoring

Identity events are monitored using:

- Microsoft Entra audit logs
- Sign-in logs
- Azure Monitor
- Microsoft Defender
- Microsoft Sentinel

---

# Compliance

The identity architecture supports:

- Zero Trust
- Identity Governance
- Access Reviews
- Audit logging
- Regulatory compliance
- Secure access management

---

# Future Enhancements

Planned improvements include:

- Expanded passwordless authentication
- Automated identity lifecycle
- Risk-based adaptive access
- Enhanced external collaboration
- Identity analytics
- Deeper Microsoft Graph integration

---

# Related Documentation

- Enterprise Solution Architecture
- Azure Deployment Architecture
- Security Architecture
- Governance Framework
- Operations Guide

---

# Revision History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | August 2026 | Initial release |

---

**Maintained by:** Talent Bridge BD Technology Team
