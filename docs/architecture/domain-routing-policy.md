# TBBD Domain & Routing Policy

## Purpose

This document defines the authoritative hostname ownership and routing policy for Talent Bridge BD (TBBD).

The purpose is to prevent hostname conflicts between the public website, employee platform, employer platform, AI services, legal services, and legacy systems.

## Canonical Domain Map

| Domain | Purpose | Status |
|---|---|---|
| `talentbridgebd.com` | Public TBBD Website | Active |
| `www.talentbridgebd.com` | Public TBBD Website | Active |
| `portal.talentbridgebd.com` | **Employee Workplace Hub** | Active |
| `talentbot.talentbridgebd.com` | **TBBD TalentBot AI** | Active |
| `employer.talentbridgebd.com` | **Employer Portal** | Reserved / Future |
| `hr.talentbridgebd.com` | **HR Services / Legacy HR namespace** | Legacy / Reserved |
| `legal.talentbridgebd.com` | **Legal / Privacy / Terms** | Reserved / Future |

## Employee Platform

The canonical employee-facing hostname is:

`portal.talentbridgebd.com`

Production traffic follows:

`portal.talentbridgebd.com`
→ Azure Front Door
→ `tbbd-portal`
→ `TBBD-Portal-Route`
→ `TBBD-Auth-OriginGroup`
→ `TBBD-HR-Portal-Origin`
→ `TBBD-HR-Portal`

Microsoft Entra ID provides authentication.

No alternative hostname should become the canonical employee portal URL.

## Employer Portal

The hostname:

`employer.talentbridgebd.com`

is exclusively reserved for the future Employer Portal.

It must not be assigned to `TBBD-HR-Portal`.

It must not be used as an alias for `portal.talentbridgebd.com`.

When implemented, the Employer Portal should have its own Front Door route and application backend.

## HR Namespace

The hostname:

`hr.talentbridgebd.com`

is a legacy HR hostname associated with the former EventMachine environment.

It must not be repurposed as the canonical employee portal.

It may be retained as an HR-specific namespace for a future architecture decision, subject to dependency and security review.

## TalentBot AI

The hostname:

`talentbot.talentbridgebd.com`

is dedicated to TBBD TalentBot AI.

It is independent from the employee Workplace Hub hostname.

## Legal

The hostname:

`legal.talentbridgebd.com`

is reserved for legal, privacy, terms, notices, and related compliance content.

## Technical App Service Hostname

The hostname:

`tbbd-hr-portal.talentbridgebd.com`

is an existing technical App Service hostname.

It is not the canonical employee-facing URL.

The canonical public employee URL remains:

`portal.talentbridgebd.com`

## Legacy Hostnames

The following are legacy and are not part of the new employee architecture:

- `hr.talentbridgebd.com`
- `eventmachine.loyaltrademanagement.com`

The legacy EventMachine must remain isolated from the new Workplace Hub.

Legacy resources and hostname bindings must not be removed until dependency checks are complete.

## Architecture Rules

1. `portal.talentbridgebd.com` means Employee Workplace Hub.
2. `employer.talentbridgebd.com` means Employer Portal.
3. `hr.talentbridgebd.com` must not become a second employee portal URL.
4. `talentbot.talentbridgebd.com` means TalentBot AI.
5. `legal.talentbridgebd.com` means Legal / Privacy / Terms.
6. No wildcard routing may send unrelated TBBD subdomains to `TBBD-HR-Portal`.
7. The Employer Portal must have a separate application boundary.
8. Legacy EventMachine hostnames must not be reused for new production services without explicit architecture approval.
9. Azure Front Door is the global application entry point.
10. Southeast Asia is the primary application region.
11. No second application region or new authentication region is required by the current architecture.

## Authoritative Employee Route

Internet
→ Azure Front Door
→ `portal.talentbridgebd.com`
→ `TBBD-Portal-Route`
→ `TBBD-HR-Portal`
→ Microsoft Entra ID
→ Workplace Hub

## Future Employer Route

Internet
→ Azure Front Door
→ `employer.talentbridgebd.com`
→ Future Employer Portal route
→ Future Employer Portal application

The Employer Portal must not share the employee portal hostname.

## Domain Ownership Principle

Each business audience receives a distinct hostname:

- Public visitors → `talentbridgebd.com`
- Employees → `portal.talentbridgebd.com`
- Employers → `employer.talentbridgebd.com`
- AI → `talentbot.talentbridgebd.com`
- Legal / compliance → `legal.talentbridgebd.com`
- Legacy HR → `hr.talentbridgebd.com`

This document is the authoritative TBBD hostname strategy.
