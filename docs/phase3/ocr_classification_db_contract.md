# Phase 3 — OCR & Classification Database Interaction Contract (v1.0)

## Purpose
This document defines the **strict database interaction boundaries**
for OCR and document classification components.

These components are **stateless processors**, not data owners.

---

## Database Access Rules

### Allowed Access

OCR and Classification MAY:

- Read from `documents` table:
  - document_id
  - source_file_name
  - storage reference (logical)

They MAY NOT rely on any other table.

---

### Forbidden Access (Critical)

OCR and Classification MUST NOT:

- INSERT into any table
- UPDATE any table
- DELETE from any table
- Write OCR output to the database
- Write classification results directly to the database
- Access comparison, exception, summary, or audit tables

All persistence is handled by downstream components.

---

## Data Flow Rule

OCR and Classification output is passed:
- In-memory
- Or via workflow payloads

Never persisted as authoritative data.

---

## Failure Semantics

- Database read failure → OCR/classification fails
- No retries without explicit workflow control
- No fallback to cached data

---

## Security Boundary

- OCR/classification DB credentials are READ-ONLY
- No schema modification privileges
- No access to audit logs

---

## Contract Stability

This contract is frozen for Phase 3.
Any change requires explicit versioning.