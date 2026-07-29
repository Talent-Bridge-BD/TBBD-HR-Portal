# Security Policy

## Overview

TBBD HR Portal is committed to maintaining the confidentiality, integrity, and availability of enterprise systems, data, and services.

This repository follows secure software development practices aligned with Microsoft Azure, Microsoft Entra ID, GitHub, and enterprise DevSecOps principles.

---

# Supported Versions

| Version | Supported |
|---------|-----------|
| Main Branch | ✅ Yes |
| Development Branch | ✅ Yes |
| Legacy Releases | ❌ No |

---

# Security Principles

The project follows these core security principles:

- Least Privilege Access
- Zero Trust Architecture
- Multi-Factor Authentication (MFA)
- Role-Based Access Control (RBAC)
- Secure by Design
- Defense in Depth
- Secure Software Development Lifecycle (SSDLC)
- Continuous Security Monitoring

---

# Platform Security

Security controls include:

- Microsoft Entra ID authentication
- Azure Role-Based Access Control (RBAC)
- Azure Key Vault for secrets
- Secure CI/CD pipelines
- GitHub Secret Scanning
- GitHub Dependabot
- Code Scanning
- Audit Logging
- Infrastructure as Code validation

---

# Secure Development

Contributors should:

- Never commit passwords or secrets.
- Never store API keys in source code.
- Use environment variables for configuration.
- Keep dependencies updated.
- Review pull requests before merging.
- Follow secure coding standards.

---

# Vulnerability Reporting

If you discover a security vulnerability, please do not disclose it publicly.

Report security issues privately to the repository maintainers.

Please include:

- Description of the issue
- Steps to reproduce
- Potential impact
- Suggested mitigation (if available)

---

# Responsible Disclosure

We appreciate responsible disclosure and will investigate all valid reports as quickly as possible.

Please allow reasonable time for investigation and remediation before public disclosure.

---

# Compliance

This repository follows enterprise governance and security practices, including:

- Microsoft Security Best Practices
- Azure Security Recommendations
- GitHub Security Best Practices
- DevSecOps Principles
- Enterprise Governance Standards

---

# Administrative Accounts

Repository administration is performed using designated administrative and automation accounts.

### LTBD-Admin

Responsible for:

- Organization governance
- Repository administration
- Enterprise security
- Policy management
- Access management

### MoazzemHossain-bot

Responsible for:

- GitHub Actions
- CI/CD automation
- Deployment automation
- Scheduled workflows
- Repository automation

These accounts are used exclusively for administrative and automation purposes and are not part of the application runtime.

---

# Security Resources

Repository security features include:

- GitHub Security Advisories
- Dependabot Alerts
- Secret Scanning
- Code Scanning
- Security Reviews

---

©️ 2026 Loyal Trade Management Ltd (LTBD). All rights reserved.
