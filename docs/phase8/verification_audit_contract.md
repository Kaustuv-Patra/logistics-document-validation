# Phase 8 — Verification PDF & Audit Artifacts Contract (v1.0)

## Purpose
This document defines the authoritative contract for:
- Verification PDF generation
- Audit artifact persistence

These artifacts provide **explainability, traceability, and legal defensibility**.

---

## Verification PDF — Role

The verification PDF is a **read-only explanation artifact**.

It explains:
- What data was extracted
- What data was expected
- Where mismatches occurred
- What decision was taken

It does NOT influence decisions.

---

## Verification PDF — Allowed Content

The PDF MAY include:

### Header
- document_id
- document_type (BOL / POD)
- shipment_id
- decision outcome
- decision timestamp

### Summary Section
- total_fields
- matched_fields
- hard_failures
- soft_failures
- missing_fields
- kv_completeness

### Field-Level Table
For each field:
- field_key
- doc_value
- master_value
- system_value (if any)
- match_status
- severity

### Decision Section
- final decision (approve / override / reject)
- decision actor role
- justification text (if provided)

---

## Verification PDF — Forbidden Content (Critical)

The PDF MUST NOT include:

- Raw OCR text blocks
- Bounding boxes or coordinates
- Confidence scores
- Internal rule logic
- Hidden or discarded fields
- Any editable elements

PDF is **output-only** and **non-interactive**.

---

## PDF Generation Rules

- Generated only AFTER final decision
- Generated from comparison + decision snapshot
- Regeneration must produce identical output
- PDF never feeds back into workflow

---

## Audit Artifacts — Role

Audit artifacts are the **system of record**.

They capture:
- What happened
- Who did it
- When it happened
- What changed

---

## Audit Write Rules

Audit writer MUST:

- Append one record per event
- Never update or delete records
- Capture before/after state snapshots
- Capture actor identity and role
- Capture event type and timestamp

---

## Audit Events Covered

Audit artifacts MUST be written for:

- document_ingested
- ocr_started / completed / failed
- kv_extraction_started / completed / failed
- comparison_started / completed / failed
- validation_summary_created / failed
- workflow_routed
- human_decision_submitted
- verification_pdf_generated

---

## Failure Semantics

- If audit write fails → operation MUST fail
- If PDF generation fails → decision remains valid, PDF retriable
- No silent audit loss permitted

---

## Determinism Requirement

Given:
- identical comparison data
- identical decision data

Verification PDF and audit records MUST be identical on regeneration.

---

## Contract Stability

This contract is frozen for Phase 8.
Any change requires explicit versioning.
