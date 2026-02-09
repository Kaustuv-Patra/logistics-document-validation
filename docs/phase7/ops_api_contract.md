# Phase 7 — Ops UI → Backend API Contract (v1.0)

## Purpose
This document defines the strict interaction contract between
the Ops UI and backend services.

The Ops UI is a **decision surface**, not a processing engine.

---

## Authentication Boundary

- All API calls require authenticated context
- Role (Reviewer / Supervisor / Auditor) is derived from token
- UI never infers permissions client-side

---

## Read Operations (Allowed)

Ops UI MAY perform the following read-only operations:

### Fetch Review Queue
Returns documents awaiting human action.

Includes:
- document_id
- document_type
- shipment_id
- document_state
- validation_summary

---

### Fetch Document Details
Returns full review context for a single document.

Includes:
- validation summary
- field-level comparison records
- verification PDF reference
- existing exceptions
- audit trail (role-gated)

---

## Write Operations (Allowed)

### Submit Decision
Allows Ops users to submit a decision.

Required inputs:
- document_id
- decision ∈ {APPROVE, REJECT, OVERRIDE}
- acknowledgement flags
- justification (mandatory for OVERRIDE)

Effects:
- Triggers workflow routing
- Emits audit record
- Does not mutate factual data

---

## Forbidden Operations (Critical)

Ops UI MUST NOT:

- Submit modified field values
- Update comparison records
- Write to master data
- Change severity levels
- Call internal workflow endpoints directly
- Perform bulk decisions

---

## Idempotency & Safety

- Decision submission is idempotent per document
- Duplicate submissions are rejected
- UI must handle read-after-write refresh only

---

## Error Handling

- Authorization failure → UI displays access denied
- Validation failure → UI displays actionable error
- System failure → UI enters read-only mode

---

## Audit Boundary

All write operations MUST result in:
- One audit record
- One state transition (or explicit failure)

No silent failures permitted.

---

## Contract Stability

This contract is frozen for Phase 7.
Any change requires explicit versioning.
