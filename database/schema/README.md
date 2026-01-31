# Database Schema — Logistics Document Validation

## Purpose
This schema is the authoritative persistence layer for the
comparison-based KV validation system.

It stores:
- Documents (metadata only)
- Field-level comparisons (DOC vs MASTER vs SYSTEM)
- Validation summaries
- Exceptions
- Audit logs

## Non-Negotiable Rules

1. This schema is **DDL-only**
   - No data is inserted manually
   - No triggers, functions, or views are allowed

2. **Immutability**
   - Raw documents, KV comparisons, exceptions, and audits are append-only
   - No update-in-place of factual data is permitted

3. **No Truth Overwrites**
   - DOC, MASTER, and SYSTEM values are stored separately
   - No column represents a “final truth” value

4. **Schema Governance**
   - Any schema change requires a new version (e.g., v1.1)
   - Existing columns and semantics must never be altered

5. **Execution Boundary**
   - This schema is not executed until Phase 2+
   - Phase 1 is structure-only

## Source of Truth
This schema is derived directly from frozen design contracts
(Steps 1–11) and must not drift from them.