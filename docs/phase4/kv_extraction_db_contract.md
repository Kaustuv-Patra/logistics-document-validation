# Phase 4 — KV Extraction Database Interaction Contract (v1.0)

## Purpose
This document defines the **strict database interaction boundaries**
for the KV extraction component.

KV extraction is a **pure transformer**, not a persistence layer.

---

## Database Access Rules

### Allowed Access

KV extraction MAY:

- Read from `kv_field_definitions`
  - field_key
  - document_type
  - data_type
  - mandatory
  - hard_validation

This read access is required only to enforce schema governance.

---

### Forbidden Access (Critical)

KV extraction MUST NOT:

- INSERT into any table
- UPDATE any table
- DELETE from any table
- Write extracted KV data to the database
- Write comparison, exception, summary, or audit records
- Modify document state

All persistence is handled by downstream components.

---

## Data Flow Rule

Extracted KV output is passed:
- In-memory
- Or via workflow payloads

It is never persisted directly by this component.

---

## Failure Semantics

- Database read failure → extraction fails
- No retries without explicit workflow control
- No fallback to cached schema definitions

---

## Security Boundary

- KV extraction DB credentials are READ-ONLY
- No schema modification privileges
- No access to audit logs

---

## Contract Stability

This contract is frozen for Phase 4.
Any change requires explicit versioning.
