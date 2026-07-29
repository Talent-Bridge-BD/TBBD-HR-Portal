# Security Policy

## Overview

TBBD HR Portal is committed to maintaining the confidentiality, integrity, and availability of enterprise systems, applications, data, and services.

This repository follows secure software development practices aligned with:

- Microsoft Azure Security Best Practices
- Microsoft Entra ID Security Standards
- GitHub Security Best Practices
- Enterprise DevSecOps Principles
- Secure Software Development Lifecycle (SSDLC)

---

# Supported Versions

| Version | Supported |
|---------|-----------|
| Main Branch | ✅ Yes |
| Development Branch | ✅ Yes |
| Legacy Releases | ❌ No |

Security updates and vulnerability fixes are provided for actively maintained branches.

---

# Security Principles

TBBD HR Portal follows these core security principles:

- Least Privilege Access
- Zero Trust Architecture
- Multi-Factor Authentication (MFA)
- Role-Based Access Control (RBAC)
- Secure by Design
- Defense in Depth
- Secure Software Development Lifecycle (SSDLC)
- Continuous Security Monitoring
- Identity-First Security
- Automated Security Validation

---

# Platform Security

Security controls include:

## Identity and Access Management

- Microsoft Entra ID authentication
- Conditional Access policies
- Multi-Factor Authentication
- Role-Based Access Control (RBAC)
- Identity governance
- Privileged access management

## Application Security

- Secure application development practices
- Dependency security monitoring
- Code review processes
- Secure API design
- Input validation
- Secure configuration management

## Cloud Security

- Azure Role-Based Access Control
- Azure Key Vault secret management
- Azure Monitor logging
- Microsoft Defender for Cloud
- Infrastructure as Code validation
- Secure Azure resource configuration

## DevSecOps Security

- GitHub Secret Scanning
- GitHub Dependabot
- GitHub Code Scanning
- Secure CI/CD pipelines
- Automated security checks
- Pull request security reviews

---

# Secure Development Practices

Contributors and maintainers must follow secure development practices.

## Do:

- Keep dependencies updated
- Review pull requests before merging
- Use secure coding standards
- Protect sensitive information
- Use environment variables for configuration
- Follow approved architecture patterns
- Report security issues responsibly

## Do Not:

- Commit passwords or credentials
- Store API keys in source code
- Upload secrets to repositories
- Disable security controls
- Bypass security review processes

---

# Vulnerability Reporting

If you discover a security vulnerability, please do not disclose it publicly.

Report security issues privately to the repository maintainers.

Please include:

- Description of the vulnerability
- Affected component
- Steps to reproduce
- Potential impact
- Suggested mitigation (if available)
- Supporting evidence where appropriate

---

# Security Contact

Security issues should be reported through:

- GitHub Security Advisories
- Private vulnerability reporting
- Organization security channels

Repository:

https://github.com/Talent-Bridge-BD/TBBD-HR-Portal

---

# Responsible Disclosure

TBBD appreciates responsible disclosure from security researchers, contributors, and community members.

We will:

- Review reported vulnerabilities
- Validate security findings
- Prioritize remediation based on impact
- Communicate updates when appropriate

Please allow reasonable time for investigation and remediation before public disclosure.

---

# Compliance and Governance

TBBD HR Portal follows enterprise governance, security, and compliance practices aligned with:

- Microsoft Security Best Practices
- Azure Security Recommendations
- Microsoft Defender for Cloud
- Microsoft Entra ID Security Controls
- GitHub Security Best Practices
- DevSecOps Principles
- Enterprise Governance Standards

---

# Security Monitoring

Security monitoring includes:

- Audit logging
- Repository security reviews
- Dependency monitoring
- Vulnerability assessment
- CI/CD security validation
- Cloud security monitoring
- Access reviews

---

# Administrative Accounts

Repository administration is performed using designated administrative and automation identities.

## LTBD-Admin

Primary administrative identity responsible for:

- Organization governance
- Repository administration
- Enterprise security management
- Policy management
- Access management
- Platform configuration

---

## MoazzemHossain-bot

Automation identity responsible for:

- GitHub Actions
- CI/CD automation
- Deployment automation
- Scheduled workflows
- Repository automation
- Operational automation

---

Administrative identities are used exclusively for governance and automation purposes and are not part of application runtime operations.

---

# Security Ownership

Security governance is managed by:

**Organization**

Talent-Bridge-BD

**Company**

Loyal Trade Management Ltd. (LTBD)

**Repository**

TBBD-HR-Portal

Security responsibilities:

- Platform security governance
- Repository protection
- Access control management
- Secure development practices
- Security improvement planning

---

# Security Resources

Repository security features include:

- GitHub Security Advisories
- Dependabot Alerts
- Secret Scanning
- Code Scanning
- Security Reviews
- Pull Request Security Checks

---

# License

Copyright (c) 2026 Loyal Trade Management Ltd. (LTBD)

All rights reserved.
