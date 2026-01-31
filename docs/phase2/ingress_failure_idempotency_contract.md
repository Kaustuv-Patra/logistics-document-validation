# Phase 2 — Ingress Failure & Idempotency Contract (v1.0)

## Purpose
This document defines deterministic behavior for ingress under
failures, retries, and duplicate submissions.

Ingress must be predictable and safe under repeated requests.

---

## Idempotency Model

- Ingress is **NOT idempotent by default**
- Each successful upload creates a new `document_id`
- Clients must not assume retry = same document

Optional future enhancement:
- Client-supplied idempotency key (out of scope for Phase 2)

---

## Duplicate Upload Handling

- Duplicate files are treated as independent uploads
- No hash-based deduplication is performed
- Deduplication, if required, happens in later phases

---

## Failure Categories

### 1. Client Errors (4xx)
- Invalid authentication
- Unsupported file type
- Missing required metadata

→ Request rejected, no storage write attempted

---

### 2. Storage Failures
- Raw storage write failure
- Partial write detection

→ Request fails  
→ No database insert committed

---

### 3. Database Failures
- Metadata insert failure
- Constraint violation

→ Request fails  
→ Stored binary must be considered orphaned and flagged for cleanup (future phase)

---

## Retry Semantics

- Ingress does not auto-retry failed requests
- Client retries are allowed and result in new document_ids
- All failures are logged explicitly

---

## Atomicity Guarantees

- Success = binary stored AND metadata persisted
- Failure = no guarantees; client must retry explicitly
- No background reconciliation in Phase 2

---

## Audit Emission

Ingress emits audit events for:
- upload_attempt
- upload_success
- upload_failure

Ingress emits NO validation or business events.

---

## Contract Stability

This contract is frozen for Phase 2.
Any change requires explicit versioning.