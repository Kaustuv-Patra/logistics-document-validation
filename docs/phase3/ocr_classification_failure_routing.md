# Phase 3 — OCR & Classification Failure Routing Contract (v1.0)

## Purpose
This document defines deterministic routing and document
state effects for OCR and document classification outcomes.

OCR and classification never make business decisions, but
they do influence **control flow**.

---

## Entry Preconditions

- Document state: INGESTED
- Raw document stored successfully
- Metadata persisted

No other entry states are allowed.

---

## OCR Outcomes & Routing

### OCR Success
Conditions:
- OCR completes without system error

Effects:
- Document state advances to OCR_COMPLETED
- OCR output passed forward (non-persistent)

---

### OCR Failure
Conditions:
- Engine crash
- Unsupported image format
- Corrupt file

Effects:
- Document state remains INGESTED
- Retry allowed via workflow
- Failure event emitted
- No state advancement

---

## Classification Outcomes & Routing

### Classification Success (High Confidence)
Conditions:
- document_type resolved as BOL or POD
- confidence ≥ configured threshold

Effects:
- Document state advances to CLASSIFIED
- document_type becomes available to downstream stages
- No database write at this stage

---

### Classification Low Confidence
Conditions:
- document_type detected but confidence < threshold

Effects:
- Document routed to IN_REVIEW
- Exception raised: DOC_STRUCT_UNSUPPORTED_TYPE
- No auto-progression

---

### Classification Failure
Conditions:
- No document_type detected
- Conflicting signals

Effects:
- Document routed to IN_REVIEW
- HARD exception raised
- No retries without human intervention

---

## Forbidden Transitions

- OCR_COMPLETED → VALIDATED
- CLASSIFIED → VALIDATED
- INGESTED → CLASSIFIED (skipping OCR)

All transitions must follow the frozen state machine.

---

## Audit Emission

The following events MUST be audited:

- ocr_started
- ocr_succeeded
- ocr_failed
- classification_started
- classification_succeeded
- classification_failed

No validation or shipment events emitted here.

---

## Contract Stability

This contract is frozen for Phase 3.
Any change requires explicit versioning.