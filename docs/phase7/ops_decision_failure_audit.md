# Phase 7 — Ops Decision Failure Handling & Audit Guarantees (v1.0)

## Purpose
This document defines deterministic behavior when
human-in-the-loop decisions succeed, fail, or are retried,
and the mandatory audit guarantees for each case.

Human decisions are **high-risk actions** and must be
fully traceable.

---

## Decision Submission Outcomes

### Decision Accepted
Conditions:
- Authorization valid
- Document in IN_REVIEW state
- All mandatory acknowledgements provided

Effects:
- Workflow routing triggered
- Document and shipment states updated per decision
- Audit record appended

---

### Decision Rejected (Validation Error)
Conditions:
- Missing acknowledgement
- Invalid decision type
- Document not in IN_REVIEW

Effects:
- No state change
- No workflow triggered
- Audit event: decision_rejected_validation

---

### Decision Failed (System Error)
Conditions:
- Database write failure
- Workflow engine unavailable
- Audit sink unavailable

Effects:
- No state change
- Decision not persisted
- UI receives retryable error
- Audit event: decision_failed_system

---

## Retry Semantics

- Ops users MAY retry failed decisions
- Duplicate submissions for already-decided documents are rejected
- Retries are logged explicitly

No silent retries are permitted.

---

## Partial Failure Rules (Critical)

- If audit write fails → decision MUST fail
- If state update fails → decision MUST fail
- If workflow trigger fails → decision MUST fail

There is **no partial success** for human decisions.

---

## Audit Record Requirements

Every decision attempt MUST emit:

- document_id
- actor_id
- actor_role
- decision_type
- timestamp
- outcome (accepted / rejected / failed)
- justification (if provided)
- before_state snapshot
- after_state snapshot (if any)

Audit records are append-only and immutable.

---

## Visibility Rules

- Ops users can see only their own failed attempts
- Supervisors can see team-level failures
- Auditors can see all attempts

---

## Determinism Requirement

Given:
- identical document state
- identical decision input

The system MUST produce identical acceptance or rejection outcomes.

---

## Contract Stability

This contract is frozen for Phase 7.
Any change requires explicit versioning.
