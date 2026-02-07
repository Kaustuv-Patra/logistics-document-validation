# Phase 4 — KV Extraction Contract (v1.0)

## Purpose
This document defines the strict responsibilities and boundaries
of the KV extraction component.

KV extraction converts **OCR signals** into **schema-bound DOC KV pairs**.
It does not decide correctness.

---

## Entry Preconditions

KV extraction is invoked only when:

- Document state = CLASSIFIED
- Document type ∈ {BOL, POD}
- OCR output is available (non-authoritative)

No other entry state is permitted.

---

## Allowed Responsibilities

KV extraction MAY:

1. Consume OCR text blocks and bounding boxes
2. Use deterministic techniques:
   - Regex
   - Named Entity Recognition
   - Spatial heuristics
3. Map extracted values to **approved schema field_keys**
4. Emit DOC-layer KV records with:
   - field_key
   - doc_value
   - extraction confidence
5. Explicitly mark fields as MISSING when not found

---

## Forbidden Responsibilities (Critical)

KV extraction MUST NOT:

- Invent or infer values
- Access master data
- Perform validation or comparison
- Decide match/mismatch
- Persist data directly to the database
- Modify document state
- Bypass the schema registry

---

## Schema Registry Enforcement

- All extracted field_keys MUST exist in `kv_field_definitions`
- Unknown fields are discarded
- Mandatory vs optional is not decided here

Schema registry is the **single source of field truth**.

---

## Output Contract (DOC KV Only)

KV extraction outputs a collection of records:

```json
{
  "field_key": "<string>",
  "doc_value": "<string | null>",
  "confidence": <0.0 – 1.0>,
  "status": "PRESENT | MISSING"
}