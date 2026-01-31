# Phase 2 — Ingress & Storage Contract (v1.0)

## Purpose
This document defines the strict behavioral contract for
document ingress and raw storage.

Ingress is a **boundary**, not a processor.

---

## Ingress Responsibilities (Allowed)

1. Accept document uploads (PDF / image)
2. Generate a unique `document_id`
3. Capture basic metadata:
   - original file name
   - upload timestamp
4. Persist raw binary to storage
5. Persist document metadata to the database

---

## Ingress Responsibilities (Forbidden)

Ingress MUST NOT:

- Inspect document contents
- Perform OCR
- Classify document type
- Extract KV fields
- Validate data
- Reject documents based on content
- Mutate or overwrite existing documents

Ingress is content-agnostic.

---

## Storage Rules (Raw Layer)

1. Raw documents are immutable
2. Re-uploading a document creates a **new document_id**
3. Raw storage is write-once, read-many
4. No deletion or replacement is allowed
5. Storage paths are derived from `document_id`, not filenames

---

## Failure Semantics

- Storage failure → request fails
- Metadata persistence failure → request fails
- Partial writes are not allowed
- No retries without explicit logging

---

## Security & Access

- Ingress requires authenticated access
- Raw storage is not publicly accessible
- Downstream services have read-only access

---

## Audit Boundary

Ingress emits:
- upload event
- storage success / failure
- metadata persistence result

Ingress does NOT emit validation or business events.

---

## Contract Stability

This contract is frozen for Phase 2.
Any change requires explicit versioning (v1.1, v2.0).