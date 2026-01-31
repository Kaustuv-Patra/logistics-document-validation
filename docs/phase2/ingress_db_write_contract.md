# Phase 2 — Ingress Database Write Contract (v1.0)

## Purpose
This document defines the **only database writes** that the
Ingress component is permitted to perform.

Ingress is a **metadata writer**, not a processor.

---

## Allowed Tables (Write Access)

### 1. documents

Ingress MAY write exactly one row per upload with the following fields:

- document_id
- document_type → MUST be NULL at ingress time
- shipment_id → MAY be NULL at ingress time
- related_bol_number → NULL
- document_version → fixed default (e.g., "v1.0")
- source_file_name
- ingestion_timestamp
- overall_validation_status → MUST be set to "INGESTED"
- auto_close_eligible → FALSE
- review_required → FALSE

Ingress MUST NOT update this row after insert.

---

## Forbidden Tables (No Write Access)

Ingress MUST NOT write to:

- kv_field_definitions
- document_field_comparisons
- document_validation_summary
- document_exceptions
- document_audit_log

---

## Update & Delete Rules

- UPDATE statements are forbidden
- DELETE statements are forbidden
- Re-uploading a document requires a new insert with a new document_id

---

## Failure Semantics

- If document metadata insert fails → ingress fails
- Partial inserts are not allowed
- No retry without explicit logging

---

## Security Boundary

- Ingress DB credentials are INSERT-only
- No SELECT on comparison or audit tables
- No schema modification privileges

---

## Contract Stability

This contract is frozen for Phase 2.
Any change requires explicit versioning.