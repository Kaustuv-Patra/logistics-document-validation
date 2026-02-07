# Phase 5 — Master Data & Comparison Engine Contract (v1.0)

## Purpose
This document defines the strict responsibilities and boundaries
of the Master Data Adapter and the Comparison Engine.

These components reconcile **DOC KV** with **MASTER KV**
and produce **field-level comparison records**.

---

## Master Data Adapter — Responsibilities

### Allowed

The Master Data Adapter MAY:

1. Accept a shipment identifier
2. Retrieve expected shipment data from an external source
3. Normalize master values into **MASTER KV format**
4. Expose master data as read-only payloads

---

### Forbidden

The Master Data Adapter MUST NOT:

- Modify external master systems
- Persist master data internally
- Perform validation or comparison
- Apply business rules
- Cache master data across requests

Master data is **read-only and transient**.

---

## Comparison Engine — Responsibilities

### Allowed

The Comparison Engine MAY:

1. Consume DOC KV and MASTER KV payloads
2. Evaluate field-by-field comparisons
3. Apply the frozen error taxonomy (HARD / SOFT / INFO)
4. Determine match_status per field:
   - MATCH
   - MISMATCH
   - MISSING
   - DERIVED
5. Emit comparison records with:
   - doc_value
   - master_value
   - system_value (if derived)
   - severity
   - source_of_truth

---

### Forbidden

The Comparison Engine MUST NOT:

- Modify DOC KV or MASTER KV
- Change document or shipment state directly
- Persist comparison results directly
- Trigger workflows
- Override severity definitions

It is a **pure decision engine**, not a controller.

---

## Rules Registry

- All comparison rules MUST be registered centrally
- No inline or ad-hoc rules are allowed
- Severity per rule is immutable

---

## Output Contract (Comparison Records)

```json
{
  "field_key": "<string>",
  "doc_value": "<string | null>",
  "master_value": "<string | null>",
  "system_value": "<string | null>",
  "match_status": "MATCH | MISMATCH | MISSING | DERIVED",
  "severity": "HARD | SOFT | INFO",
  "source_of_truth": "DOC | MASTER | SYSTEM"
}