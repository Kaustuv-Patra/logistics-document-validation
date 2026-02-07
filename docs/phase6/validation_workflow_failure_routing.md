# Phase 6 — Validation Summary & Workflow Failure Routing (v1.0)

## Purpose
This document defines deterministic routing and state transitions
for validation summary computation and workflow orchestration.

Validation and workflow do not create facts — they only
**advance state or halt safely**.

---

## Entry Preconditions

Validation Summary execution requires:
- Document state = VALIDATED
- Comparison records available

Workflow execution requires:
- Validation summary available

No other entry states are permitted.

---

## Validation Summary Outcomes

### Summary Success
Conditions:
- Aggregation completes without error

Effects:
- Summary persisted
- Control passed to workflow routing
- No state rollback

---

### Summary Failure
Conditions:
- Aggregation error
- Comparison payload unreadable

Effects:
- Document routed to IN_REVIEW
- HARD exception raised: DOC_STRUCT_SCHEMA_VIOLATION
- No workflow routing attempted

---

## Workflow Routing Outcomes

### Auto-Close Routing
Conditions:
- auto_close_eligible = true
- hard_failures = 0
- review_required = false

Effects:
- Document state advances to CLOSED (POD) or APPROVED (BOL)
- Shipment state advanced per frozen state machine

---

### Human Review Routing
Conditions:
- review_required = true
- OR hard_failures > 0

Effects:
- Document state advances to IN_REVIEW
- Human task created
- Shipment state unchanged

---

### Workflow Failure
Conditions:
- Orchestration engine failure
- State transition write failure

Effects:
- Document state unchanged
- Retry allowed
- No partial transitions permitted

---

## Forbidden Transitions

- VALIDATED → ARCHIVED (without decision)
- CLOSED → IN_REVIEW
- APPROVED → VALIDATED

All transitions must follow the frozen state machine.

---

## Audit Emission

The following events MUST be audited:

- validation_summary_failed
- workflow_auto_close_routed
- workflow_human_review_routed
- workflow_failed

---

## Determinism Requirement

Given:
- identical summary payload
- identical state machine rules

Routing and state transitions MUST be identical.

---

## Contract Stability

This contract is frozen for Phase 6.
Any change requires explicit versioning.
