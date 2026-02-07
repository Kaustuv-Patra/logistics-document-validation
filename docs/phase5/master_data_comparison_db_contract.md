# Phase 5 — Master Data & Comparison Engine Database Interaction Contract (v1.0)

## Purpose
This document defines the **strict database interaction boundaries**
for the Master Data Adapter and Comparison Engine.

These components are **decision and reconciliation layers**, not
persistence layers.

---

## Database Access Rules

### Allowed Access

Master Data Adapter and Comparison Engine MAY:

- Read from `documents` table:
  - document_id
  - shipment_id
  - document_type

- Read from `kv_field_definitions`:
  - field_key
  - document_type
  - data_type
  - mandatory
  - hard_validation

These reads are required only to contextualize comparisons.

---

### Forbidden Access (Critical)

These components MUST NOT:

- INSERT into any table
- UPDATE any table
- DELETE from any table
- Persist comparison results directly
- Write exceptions, summaries, or audit records
- Modify document or shipment state

All persistence is handled by downstream orchestration layers.

---

## Data Flow Rule

Comparison outputs are passed:
- In-memory
- Or via workflow payloads

They are never written directly by these components.

---

## Failure Semantics

- Database read failure → comparison fails
- No retries without explicit workflow control
- No fallback to cached data

---

## Security Boundary

- DB credentials are READ-ONLY
- No schema modification privileges
- No access to audit logs

---

## Contract Stability

This contract is frozen for Phase 5.
Any change requires explicit versioning.