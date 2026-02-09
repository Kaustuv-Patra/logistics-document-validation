# Reliability NFRs (v1.0)

## Purpose
This document defines how the system behaves under failures
and partial outages.

The system must fail **safe**, never **silent**.

---

## Failure Principles

- No data corruption is acceptable
- Partial success is forbidden for decisions
- Failures must be explicit and auditable

---

## Component Failure Handling

| Component | Failure Behavior |
|---------|------------------|
| Ingress | Reject request |
| OCR | Retry allowed |
| KV Extraction | Route to review |
| Comparison | Route to review |
| Workflow | Retry, no state change |
| Audit | Fail operation |

---

## Data Durability

- All persisted records are append-only
- No background reconciliation without audit
- No automatic data repair

---

## Disaster Recovery Assumption

- Backup/restore is out of scope here
- Architecture must not prevent recovery
