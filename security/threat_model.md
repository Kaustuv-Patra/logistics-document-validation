# Threat Model & Abuse Cases (v1.0)

## Purpose
This document identifies credible security threats and abuse cases
for the logistics document validation system and defines mandatory
mitigations.

The system assumes **hostile input** and **curious insiders**.

---

## Threat Actors

1. External attacker (unauthenticated)
2. Authenticated but unauthorized user
3. Malicious insider (Ops role)
4. Compromised system component
5. Accidental operator error

---

## Assets to Protect

- Raw documents
- Extracted KV data
- Master shipment data
- Validation decisions
- Audit logs
- Workflow state

---

## Threat Categories & Mitigations

### 1. Unauthorized Data Access
Threat:
- Accessing documents or data without permission

Mitigations:
- RBAC enforced server-side
- Least-privilege DB credentials
- No public access to raw storage

---

### 2. Data Tampering
Threat:
- Modifying extracted values, comparisons, or audit logs

Mitigations:
- Append-only persistence
- No update/delete permissions
- Audit snapshots on every action

---

### 3. Privilege Escalation
Threat:
- Reviewer acting as Supervisor
- Bypassing HARD validation

Mitigations:
- Explicit role checks
- Supervisor-only override endpoints
- Mandatory justification & audit

---

### 4. Replay / Duplicate Attacks
Threat:
- Replaying decisions or uploads

Mitigations:
- Decision idempotency per document
- Duplicate decision rejection
- Explicit audit of retries

---

### 5. Denial of Service
Threat:
- Flooding ingress or review queue

Mitigations:
- Rate limiting (future)
- Async workflows
- Back-pressure via queues

---

### 6. Malicious Documents
Threat:
- PDFs exploiting OCR or rendering engines

Mitigations:
- Content-agnostic ingress
- Sandboxed OCR execution (future)
- No PDF execution or scripting

---

### 7. Audit Suppression
Threat:
- Performing actions without audit trail

Mitigations:
- Fail operation if audit write fails
- No bypass paths
- Auditor read-only access

---

## Abuse Scenarios (Explicit)

| Scenario | Expected System Behavior |
|--------|--------------------------|
| Reviewer tries HARD override | Request denied |
| Supervisor omits justification | Request denied |
| OCR crash | Retry, no state change |
| Audit store unavailable | Operation fails |
| Duplicate decision submit | Rejected |

---

## Residual Risk Acceptance

- OCR misreads are accepted as non-authoritative
- Human error is mitigated via audit, not elimination

---

## Contract Stability

This threat model is frozen for Phase 9.
Any change requires explicit versioning.
