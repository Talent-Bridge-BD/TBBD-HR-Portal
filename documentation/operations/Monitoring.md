# Monitoring

> Monitoring and observability framework for the TBBD HR Portal platform across Microsoft Azure, Microsoft 365, Microsoft Entra ID, Azure AI services, applications, and security operations.

---

# Document Information

| Property | Value |
|----------|-------|
| Repository | TBBD-HR-Portal |
| Document | Monitoring |
| Version | v1.0.0 |
| Owner | Talent Bridge BD Technology Team |
| Classification | Internal Enterprise Documentation |
| Last Updated | August 2026 |

---

# Overview

The TBBD HR Portal monitoring framework provides visibility into platform health, application performance, security events, and operational activities.

The monitoring approach follows Microsoft cloud monitoring best practices and supports proactive issue detection, troubleshooting, and continuous improvement.

---

# Monitoring Objectives

The monitoring framework aims to:

- Detect service issues early
- Maintain application availability
- Monitor security events
- Improve operational visibility
- Support incident response
- Track system performance
- Enable data-driven improvements

---

# Monitoring Architecture

```text
TBBD HR Portal

        │

        ▼

Application & Platform Services

        │

 ┌──────┼────────┐

 ▼      ▼        ▼

Azure   Microsoft   Security
Monitor 365         Monitoring

        │

        ▼

Log Analytics Workspace

        │

 ┌──────┼────────┐

 ▼      ▼        ▼

Application Insights

Microsoft Sentinel

Defender for Cloud
```

---

# Monitoring Services

## Azure Monitor

Azure Monitor provides:

- Infrastructure monitoring
- Application monitoring
- Metrics collection
- Logs analysis
- Alert management

Monitored resources include:

- Azure App Services
- Azure Functions
- Storage services
- AI services
- Networking components

---

# Application Insights

Application Insights provides application-level observability.

Monitoring includes:

- Application availability
- Response times
- Exceptions
- Dependencies
- Performance issues
- User activity

Key capabilities:

- Live metrics
- Transaction tracing
- Failure analysis
- Performance diagnostics

---

# Log Analytics Workspace

Log Analytics provides centralized log collection and analysis.

Collected data may include:

- Application logs
- Authentication logs
- Security logs
- Infrastructure logs
- Integration logs

---

# Microsoft Sentinel Integration

Microsoft Sentinel provides security monitoring and threat detection.

Monitoring capabilities:

- Security incidents
- Threat detection
- Investigation workflows
- Automated responses
- Security analytics

Data sources:

- Microsoft Entra ID
- Microsoft Defender
- Azure resources
- Microsoft 365 services

---

# Microsoft Defender Monitoring

Microsoft Defender provides security posture monitoring.

Monitor:

- Security recommendations
- Vulnerabilities
- Threat alerts
- Secure score improvements
- Cloud security posture

---

# Microsoft Entra ID Monitoring

Identity monitoring includes:

- Sign-in activities
- Failed authentication attempts
- Risk detections
- Conditional Access events
- Privileged identity activities

---

# Microsoft 365 Monitoring

Monitor:

## Microsoft Teams

- Service health
- Collaboration availability
- Application integration

## SharePoint Online

- Site availability
- Access issues
- Storage utilization

## Exchange Online

- Mail flow
- Service health
- Configuration changes

---

# Azure AI Monitoring

AI services should monitor:

- API availability
- Request failures
- Usage metrics
- Performance
- Service health

Applicable services:

- Azure AI Foundry
- Azure OpenAI
- Azure AI Search
- Azure AI Services

---

# Alert Management

Alerts should be configured for:

## Availability

Examples:

- Application unavailable
- Service outage
- Endpoint failure

## Performance

Examples:

- High response time
- Resource pressure
- API failures

## Security

Examples:

- Suspicious sign-in
- Privilege changes
- Security incidents

---

# Monitoring Dashboard

Recommended dashboards:

## Platform Dashboard

Includes:

- Application health
- Azure resources
- Availability metrics

## Security Dashboard

Includes:

- Sentinel incidents
- Defender alerts
- Identity risks

## Operations Dashboard

Includes:

- Alerts
- Performance
- Service health

---

# Log Retention

Retention policies should follow:

- Security requirements
- Compliance requirements
- Business needs

Review:

- Diagnostic settings
- Workspace retention
- Audit logs

---

# Monitoring Responsibilities

| Role | Responsibility |
|------|----------------|
| Operations Team | Platform monitoring |
| Security Team | Threat monitoring |
| Developers | Application monitoring |
| Administrators | Configuration monitoring |

---

# Operational Review

Monitoring should be reviewed:

- Daily for critical systems
- Weekly for operational health
- Monthly for improvements
- Quarterly for architecture review

---

# Best Practices

Follow:

- Centralized logging
- Automated alerts
- Proactive monitoring
- Security visibility
- Continuous optimization

---

# Related Documentation

## Operations

- Operations-Guide.md
- Backup-Disaster-Recovery.md
- Incident-Response.md
- Business-Continuity.md
- Maintenance.md

## Security

- Security-Architecture.md
- Compliance.md

---

# Revision History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | August 2026 | Initial release |

---

**Maintained by:** Talent Bridge BD Technology Team
