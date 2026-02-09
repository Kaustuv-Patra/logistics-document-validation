# Security & RBAC Contract (v1.0)

## Purpose
This document defines the authoritative role-based access control (RBAC)
model for the logistics document validation system.

Security is enforced **server-side only**.
The UI is never trusted.

---

## Roles (Frozen)

### 1. System
- Non-human actor
- Executes automated workflows only

### 2. Ops Reviewer
- Human reviewer
- Handles SOFT discrepancies

### 3. Ops Supervisor
- Senior human reviewer
- Can override HARD discrepancies

### 4. Auditor
- Read-only access
- No decision authority

No additional roles are permitted in v1.0.

---

## Permission Matrix

| Action | System | Reviewer | Supervisor | Auditor |
|------|--------|----------|------------|---------|
| Upload document | ✓ | ✗ | ✗ | ✗ |
| View document | ✓ | ✓ | ✓ | ✓ |
| View comparisons | ✓ | ✓ | ✓ | ✓ |
| Approve (SOFT) | ✗ | ✓ | ✓ | ✗ |
| Override (HARD) | ✗ | ✗ | ✓ | ✗ |
| Reject document | ✗ | ✓ | ✓ | ✗ |
| View audit logs | ✗ | Limited | Full | Full |
| Modify data | ✗ | ✗ | ✗ | ✗ |

---

## Enforcement Points

RBAC MUST be enforced at:
- Backend API layer
- Workflow execution layer

RBAC MUST NOT be enforced solely in:
- UI
- Client-side logic

---

## Forbidden Capabilities (Critical)

No role may:
- Edit extracted KV values
- Edit master data
- Change severity levels
- Bypass audit logging
- Delete or modify audit records
- Re-open archived documents

---

## Privilege Escalation Rules

- No implicit escalation is allowed
- Supervisor actions must be explicit
- Overrides require justification
- All escalations are audited

---

## Token & Identity Assumptions

- Identity is externally authenticated (out of scope here)
- Tokens must carry role claims
- Backend validates role on every request

---

## Contract Stability

This RBAC contract is frozen for Phase 9.
Any change requires explicit versioning.
