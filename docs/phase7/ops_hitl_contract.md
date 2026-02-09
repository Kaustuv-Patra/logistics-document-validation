# Phase 7 — Ops UI & Human-in-the-Loop Contract (v1.0)

## Purpose
This document defines the authoritative contract for
human interaction with the system.

Humans do not create facts.
Humans make **explicit decisions on disagreements**.

---

## Roles (Frozen)

- Ops Reviewer
- Ops Supervisor
- Auditor (read-only)

No other roles exist in Phase 7.

---

## What Ops CAN See

Ops users MAY see:

### Document Context
- document_id
- document_type (BOL / POD)
- shipment_id
- document state
- validation summary metrics

### Field-Level Comparisons
- field_key
- doc_value
- master_value
- system_value (if present)
- match_status
- severity (HARD / SOFT / INFO)

### Artifacts
- Read-only verification PDF
- Audit trail (role-restricted)

---

## What Ops CANNOT See (Critical)

Ops users MUST NOT see:

- Raw OCR text blocks
- Extraction confidence scores
- Internal rule logic
- System-derived intermediate values
- Hidden or discarded fields

Opacity is intentional.

---

## Allowed Human Actions

### Ops Reviewer
- Approve document (SOFT issues only)
- Reject document
- Add structured comments

### Ops Supervisor (Additional)
- Override HARD failures
- Force document acceptance or rejection
- Resume blocked shipments

---

## Mandatory Acknowledgements

Every human decision MUST include:

- Decision type (approve / reject / override)
- Explicit acknowledgement of:
  - HARD issues (if any)
  - Impact on shipment closure
- Free-text justification (required for overrides)

No acknowledgement → no action allowed.

---

## Forbidden Human Actions

Humans MUST NOT:

- Edit extracted values
- Edit master values
- Change severity levels
- Reclassify document type
- Skip required acknowledgements
- Bulk-approve documents

Humans decide — they do not edit data.

---

## Decision Effects

| Decision | Effect |
|---|---|
| Approve | Document accepted, shipment may proceed |
| Override | HARD failures remain visible, shipment allowed |
| Reject | Document archived, shipment blocked |

All effects follow frozen state machines.

---

## Audit Guarantees

Every human action MUST emit:

- actor
- role
- decision
- timestamp
- justification
- before/after state snapshot

Audit records are append-only and immutable.

---

## Determinism Guarantee

Given:
- identical comparison data
- identical document state

The UI MUST present identical information to all users
with the same role.

---

## Contract Stability

This contract is frozen for Phase 7.
Any change requires explicit versioning.