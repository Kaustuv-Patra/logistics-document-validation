# Phase 2 — Raw Storage Path & Naming Contract (v1.0)

## Purpose
This document defines the **canonical storage layout**
for raw uploaded documents.

The layout is deterministic, immutable, and backend-agnostic.

---

## Root Storage Namespace

All raw documents are stored under a single logical root:

/storage/raw/

This root is **never exposed publicly**.

---

## Directory Structure

Raw documents are organized by document_id prefix to avoid
large flat directories:

/storage/raw/
  └── <first_2_chars_of_document_id>/
      └── <next_2_chars_of_document_id>/
          └── <document_id>/
              └── original

Example:

/storage/raw/ab/cd/abcd1234-5678-90ef-aaaa-bbbbccccdddd/original

---

## File Naming Rules

- The stored file name is always: `original`
- Original extensions are NOT preserved
- MIME type is stored in metadata, not in the path
- Filenames are never used as identifiers

---

## Immutability Rules

- Stored binaries are write-once
- No overwrite is permitted
- No delete is permitted
- Re-upload results in a new document_id and new path

---

## Access Rules

- Ingress: write-once
- Downstream services: read-only
- Ops UI: indirect access via signed URLs (future phase)

---

## Failure Semantics

- Partial writes are forbidden
- Storage failure invalidates the ingress request
- No background reconciliation is allowed

---

## Contract Stability

This contract is frozen for Phase 2.
Any change requires explicit versioning.