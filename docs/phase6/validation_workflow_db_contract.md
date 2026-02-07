# Phase 6 — Validation Summary & Workflow Database Interaction Contract (v1.0)

## Purpose
This document defines the **strict database interaction boundaries**
for Validation Summary and Workflow Orchestration components.

These components are **decision and control layers**, not data owners.

---

## Database Access Rules

### Allowed Access

Validation Summary and Workflow Orchestration MAY:

- Read from `document_field_comparisons`
  - document_id
  - field_key
  - match_status
  - severity

- Read from `documents`
  - document_id
  - document_type
  - shipment_id
  - overall_validation_status
  - review_required

---

### Allowed Writes (Controlled)

Workflow Orchestration MAY write **only** the following:

- INSERT into `document_validation_summary`
- UPDATE in `documents`:
  - overall_validation_status
  - review_required
  - auto_close_eligible

All updates must follow the frozen state machine.

---

### Forbidden Access (Critical)

These components MUST NOT:

- Modify comparison records
- Write to `kv_field_definitions`
- Write to `document_field_comparisons`
- Write to `document_exceptions`
- Write to `document_audit_log` directly
- Modify shipment master data
- Perform schema modifications

Audit persistence is handled by a dedicated audit layer.

---

## Atomicity & Consistency

- Summary write and document state update must be atomic
- Partial updates are forbidden
- Failed writes result in no state change

---

## Failure Semantics

- Database read failure → document routed to IN_REVIEW
- Database write failure → state unchanged, retry allowed
- No silent retries

---

## Security Boundary

- DB credentials are least-privilege
- Write access limited to explicitly listed columns
- No access to audit tables

---

## Contract Stability

This contract is frozen for Phase 6.
Any change requires explicit versioning.
