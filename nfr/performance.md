# Performance NFRs (v1.0)

## Purpose
This document defines the performance expectations of the system.

Performance optimizations MUST NOT compromise correctness,
auditability, or security.

---

## Ingress Performance

- Upload handling must be asynchronous
- No synchronous OCR or validation during upload
- Large documents must not block the ingress thread

---

## Processing Latency Targets (Design-Time)

- OCR & classification: async, no SLA guarantee
- KV extraction + comparison: deterministic, bounded by input size
- Validation & workflow routing: sub-second once invoked
- Human review latency: not constrained (human-dependent)

---

## Forbidden Optimizations

The system MUST NOT:
- Skip audit writes for speed
- Cache validation decisions
- Short-circuit HARD checks
- Batch human decisions

---

## Measurement Boundary

Performance is measured at:
- Component boundaries
- Workflow transitions

Not at UI render time.
