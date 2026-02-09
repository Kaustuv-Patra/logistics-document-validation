# Scalability NFRs (v1.0)

## Purpose
This document defines how the system scales with volume and load.

Scaling is achieved by **addition**, not mutation.

---

## Scaling Dimensions

The system must scale on:
- Number of documents
- Number of fields per document
- Number of concurrent reviews
- Number of shipments

---

## Architectural Guarantees

- Stateless processing components
- Horizontal scaling of workers
- No shared in-memory state
- Idempotent workflows

---

## Forbidden Scaling Techniques

The system MUST NOT:
- Introduce shared mutable caches
- Rely on single-node state
- Sacrifice audit fidelity
- Drop low-priority records silently

---

## Human Scaling

- Review queues must support sharding
- No global locks on review actions
