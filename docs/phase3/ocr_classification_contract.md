# Phase 3 — OCR & Classification Contract (v1.0)

## Purpose
This document defines the strict, non-authoritative role of
OCR and document classification within the system.

OCR and classification produce **signals**, not truth.

---

## OCR Responsibilities (Allowed)

1. Accept a reference to a raw stored document
2. Perform image preprocessing (de-skew, noise reduction)
3. Extract text blocks with bounding boxes
4. Attach confidence scores per block
5. Emit OCR output as transient data

---

## OCR Responsibilities (Forbidden)

OCR MUST NOT:

- Persist OCR text as authoritative data
- Perform validation or comparison
- Decide document correctness
- Modify raw documents
- Write to comparison or audit tables

OCR output is **ephemeral**.

---

## OCR Output Contract (Non-Persistent)

OCR emits:

- text
- bounding box coordinates
- confidence score

OCR output is passed **in-memory or via workflow**, never as truth.

---

## Document Classification Responsibilities (Allowed)

1. Consume OCR output and layout signals
2. Classify document as BOL or POD
3. Emit classification confidence

---

## Document Classification Responsibilities (Forbidden)

Classification MUST NOT:

- Extract KV fields
- Perform validation
- Override schema rules
- Change document state directly

Classification emits a **single decision**.

---

## Classification Output Contract

Classification emits:

- document_type ∈ {BOL, POD}
- confidence score

Low confidence classification MUST route to exception handling.

---

## Failure Semantics

- OCR failure → retry allowed
- Classification failure → document routed to review
- No silent fallback is permitted

---

## Audit Boundary

OCR and classification emit audit events for:
- start
- success
- failure

They emit **no business decisions**.

---

## Determinism Requirement

Given:
- same raw document
- same preprocessing parameters

OCR and classification MUST produce consistent results.

---

## Contract Stability

This contract is frozen for Phase 3.
Any change requires explicit versioning.