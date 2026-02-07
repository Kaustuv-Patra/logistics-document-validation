# Phase 6 — Validation Summary & Workflow Orchestration Contract (v1.0)

## Purpose
This document defines the strict responsibilities and boundaries
of the Validation Summary builder and Workflow Orchestration layer.

These components convert **field-level comparison results**
into **document-level decisions and routing signals**.

---

## Entry Preconditions

Validation Summary is invoked only when:

- Document state = VALIDATED (post-comparison)
- Field-level comparison records are available

Workflow Orchestration is invoked only when:

- Validation Summary output exists

No other entry states are permitted.

---

## Validation Summary — Responsibilities

### Allowed

Validation Summary MAY:

1. Aggregate field-level comparison records
2. Count:
   - total fields
   - matched fields
   - HARD failures
   - SOFT failures
   - missing fields
3. Compute:
   - kv_completeness
   - auto_close_eligible (boolean)
   - review_required (boolean)
4. Produce a **deterministic summary payload**

---

### Forbidden

Validation Summary MUST NOT:

- Modify comparison records
- Re-evaluate severities
- Change document or shipment state
- Trigger workflows directly
- Persist audit records

It is a **pure aggregation layer**.

---

## Validation Summary Output Contract

```json
{
  "total_fields": <int>,
  "matched_fields": <int>,
  "hard_failures": <int>,
  "soft_failures": <int>,
  "missing_fields": <int>,
  "kv_completeness": <0.0 – 1.0>,
  "auto_close_eligible": <boolean>,
  "review_required": <boolean>
}