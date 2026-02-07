# Phase 5 — Comparison Failure Routing & Document State Effects (v1.0)

## Purpose
This document defines deterministic routing and document
state behavior for field-level comparison outcomes.

The Comparison Engine evaluates truth discrepancies but
does not finalize business decisions.

---

## Entry Preconditions

Comparison is invoked only when:

- Document state = KV_EXTRACTED
- DOC KV payload available
- MASTER KV payload available

No other entry state is permitted.

---

## Comparison Outcomes & Routing

### Comparison Completed (No HARD Failures)
Conditions:
- All mandatory fields compared
- No HARD severity mismatches detected

Effects:
- Document state advances to VALIDATED
- Validation summary prepared downstream
- No human review triggered at this stage

---

### Comparison Completed (SOFT Failures Present)
Conditions:
- One or more SOFT severity mismatches detected
- No HARD failures

Effects:
- Document state advances to VALIDATED
- review_required = TRUE
- Routed to human review downstream

---

### Comparison Completed (HARD Failures Present)
Conditions:
- One or more HARD severity mismatches detected
- Or required master data unavailable

Effects:
- Document state advances to VALIDATED
- review_required = TRUE
- HARD exceptions raised
- Auto-close explicitly blocked

---

### Comparison Failure (System Error)
Conditions:
- Comparison engine crash
- Rules registry unavailable
- Payload corruption

Effects:
- Document routed to IN_REVIEW
- HARD exception raised: DOC_STRUCT_SCHEMA_VIOLATION
- No downstream validation summary generated

---

## Forbidden Transitions

- KV_EXTRACTED → ARCHIVED
- KV_EXTRACTED → CLOSED
- Comparison → Shipment state changes

All transitions must follow the frozen state machine.

---

## Audit Emission

Comparison MUST emit audit events for:
- comparison_started
- comparison_completed
- comparison_failed

No workflow, shipment, or financial events emitted here.

---

## Determinism Requirement

Given:
- identical DOC KV
- identical MASTER KV
- identical rule registry

Comparison routing and outcomes MUST be identical.

---

## Contract Stability

This contract is frozen for Phase 5.
Any change requires explicit versioning.