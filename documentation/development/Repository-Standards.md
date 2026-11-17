# Repository Standards

> Enterprise repository governance standards for the TBBD HR Portal GitHub
> repository covering repository structure, naming conventions, access
> management, contribution workflow, security controls, and documentation
> practices.

---

## Document Information

|Property|Value|
|----------|-------|
|Repository|TBBD-HR-Portal|
|Document|Repository Standards|
|Version|v1.0.0|
|Owner|Talent Bridge BD Technology Team|
|Classification|Internal Enterprise Documentation|
|Last Updated|August 2026|

---

## Overview

The TBBD HR Portal repository follows enterprise GitHub management practices to
ensure secure collaboration, maintainability, traceability, and consistent
software delivery.

These standards define how source code, documentation, infrastructure,
automation, and configuration resources are organized and managed.

---

## Repository Objectives

Repository standards ensure:

- Consistent project organization
- Secure source control management
- Effective team collaboration
- Controlled change management
- Improved maintainability
- Enterprise governance alignment

---

## Repository Structure

The repository follows this high-level structure:

```text
TBBD-HR-Portal

│
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   └── dependabot.yml
│
├── documentation/
│
├── infrastructure/
│   ├── bicep/
│   ├── terraform/
│   └── arm/
│
├── src/
│
├── api/
│
├── services/
│
├── assets/
│
├── scripts/
│
├── tests/
│
├── README.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

## Repository Naming Standards

### Repository Name

Standard:

```text
TBBD-HR-Portal
```

Naming principles:

- Organization prefix: TBBD
- Solution name: HR
- Platform identifier: Portal

---

## File Naming Standards

Documentation:

```text
Pascal-Case-With-Hyphen.md
```

Examples:

```text
Enterprise-Solution-Architecture.md

Security-Architecture.md

Deployment-Pipeline.md
```

---

Source code naming should follow language-specific standards.

---

## Branch Standards

Recommended branches:

```text
main

develop

feature/*

bugfix/*

hotfix/*
```

Examples:

```text
feature/employee-profile

feature/hr-copilot

bugfix/login-error

hotfix/security-update
```

---

## Main Branch Protection

The main branch should enforce:

- Pull request approval
- Required status checks
- Automated testing
- Code review
- Protected history

Direct commits to main should be restricted.

---

## Pull Request Standards

All changes should be submitted through pull requests.

Pull requests should include:

- Clear title
- Description of changes
- Testing information
- Documentation updates
- Related issue reference

---

## Commit Message Standards

Commit messages should follow:

```text
type: description
```

Examples:

```text
docs: add security architecture

feat: add employee dashboard

fix: resolve authentication issue

chore: update dependencies
```

---

## Recommended Commit Types

|Type|Usage|
|------|-------|
|feat|New functionality|
|fix|Bug correction|
|docs|Documentation|
|chore|Maintenance|
|refactor|Code improvement|
|security|Security changes|
|test|Testing changes|

---

## Access Management

Repository access follows least privilege principles.

Recommended roles:

|Role|Responsibility|
|------|----------------|
|Owner|Organization governance|
|Maintainer|Repository management|
|Developer|Code contribution|
|Reviewer|Code review|

---

## CODEOWNERS

The repository should define ownership through:

```text
.github/CODEOWNERS
```

Purpose:

- Automatic reviewer assignment
- Clear ownership
- Controlled approvals

---

## Security Controls

Repository security practices include:

- Secret scanning
- Dependency scanning
- Branch protection
- Access reviews
- Security policies
- Vulnerability management

---

## GitHub Actions Standards

CI/CD workflows should:

- Use approved actions
- Protect secrets
- Validate changes
- Run automated tests
- Support controlled deployment

Workflow location:

```text
.github/workflows/
```

---

## Documentation Standards

All major changes should update:

- README.md
- Architecture documents
- Deployment documentation
- Operational procedures

Documentation should remain synchronized with implementation.

---

## Infrastructure Standards

Infrastructure changes should use:

- Infrastructure as Code
- Version control
- Review process
- Automated validation

Supported technologies:

- Azure Bicep
- Terraform

---

## Security Review Requirements

Changes affecting:

- Identity
- Access control
- Data handling
- AI services
- Network configuration

require security review.

---

## Repository Maintenance

Regular activities:

- Dependency updates
- Documentation review
- Access review
- Security scanning
- Workflow validation

---

## Branching Strategy and Workflow

The repository uses a controlled branching model to separate production-ready
code, integration work, feature development, maintenance fixes, and release
preparation.

### Branch Model

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready code and official releases |
| `develop` | Integration development and pre-release validation |
| `feature/<name>` | Isolated development of new functionality |
| `bugfix/<name>` | Correction of non-critical defects |
| `release/<version>` | Final testing and preparation of a production release |
| `hotfix/<name>` | Urgent correction of a critical production issue |

The `develop` and `release/*` branches are part of the recommended workflow.
Their use should follow the team's approved release process.

### Feature and Bugfix Workflow

1. Create a short-lived feature or bugfix branch from the appropriate
   integration branch.
2. Make the change in isolation.
3. Commit using the repository commit-message standards.
4. Open a pull request with a clear description, testing information, and
   related issue.
5. Complete review and automated checks.
6. Merge using the approved merge strategy.

Examples:

- `feature/employee-dashboard`
- `feature/hr-copilot`
- `bugfix/login-error`
- `bugfix/api-timeout`

### Release Workflow

Create a `release/<version>` branch when preparing a planned release.

Release preparation includes:

- Final testing and validation.
- Version updates.
- Release notes and documentation updates.
- Final approval before production release.

Examples: `release/v1.1.0` and `release/v2.0.0`.

### Hotfix Workflow

For an urgent production issue:

1. Create a `hotfix/<name>` branch from `main`.
2. Implement and validate the correction.
3. Submit the change through the required review and approval process.
4. Merge the approved correction into `main`.
5. Merge or otherwise integrate the correction back into `develop` so the fix
   is retained in subsequent development.

Examples: `hotfix/security-patch` and `hotfix/service-outage`.

### Merge Strategy

The recommended merge approach is:

- Squash merge for feature branches.
- Merge commits for release integration.
- Controlled merges for hotfixes, including integration back into the
  development branch.

All merges remain subject to branch protection, pull-request review, and
required automated checks.

### Version Management

Releases follow semantic versioning:

`MAJOR.MINOR.PATCH`

- **Major:** Breaking changes.
- **Minor:** New functionality.
- **Patch:** Bug fixes and compatible corrections.

### Collaboration Rules

Contributors should:

- Keep branches short-lived.
- Write meaningful commit messages.
- Update related documentation.
- Review changes before merging.
- Follow repository security and access requirements.

## Related Documentation

### Development

- Development-Lifecycle.md
- Deployment-Pipeline.md
- Coding-Standards.md
- Release-Management.md

### Governance

- Governance-Framework.md
- Enterprise-Standards.md

---

## Revision History

| Version | Date        | Description     |
| ------- | ----------- | --------------- |
| 1.0.0   | August 2026 | Initial release |

---

**Maintained by:** Talent Bridge BD Technology Team
