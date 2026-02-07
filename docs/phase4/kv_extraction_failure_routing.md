# Phase 4 — KV Extraction Failure Routing & State Effects (v1.0)

## Purpose
This document defines deterministic routing and document
state behavior for KV extraction outcomes.

KV extraction never validates correctness, but it determines
whether downstream comparison can proceed.

---

## Entry Preconditions

KV extraction is invoked only when:

- Document state = CLASSIFIED
- Document type is resolved (BOL or POD)
- OCR output is available

No other entry state is permitted.

---

## KV Extraction Outcomes & Routing

### Successful Extraction
Conditions:
- Extraction process completes without system error
- At least one schema-approved field processed

Effects:
- Document state advances to KV_EXTRACTED
- DOC KV output passed forward (non-persistent)
- Missing fields are explicitly marked as MISSING

---

### Partial Extraction
Conditions:
- Extraction completes
- Some fields extracted, others missing

Effects:
- Document state advances to KV_EXTRACTED
- No exception raised at this stage
- Missing mandatory fields are NOT treated as errors here

---

### Extraction Failure
Conditions:
- Extraction engine crashes
- Schema registry unavailable
- OCR payload malformed

Effects:
- Document routed to IN_REVIEW
- HARD exception raised: DOC_STRUCT_SCHEMA_VIOLATION
- No downstream comparison attempted

---

## Forbidden Transitions

- CLASSIFIED → VALIDATED (skipping KV extraction)
- KV_EXTRACTED → ARCHIVED
- KV_EXTRACTED → IN_REVIEW without exception

All transitions must follow the frozen state machine.

---

## Audit Emission

KV extraction MUST emit audit events for:
- kv_extraction_started
- kv_extraction_completed
- kv_extraction_failed

No validation or shipment events are emitted.

---

## Determinism Requirement

Given:
- identical OCR output
- identical schema registry

KV extraction MUST produce identical KV outputs and routing.

---

## Contract Stability

This contract is frozen for Phase 4.
Any change requires explicit versioning.