-- ===============================
-- Logistics Document Validation
-- Authoritative Schema v1.0
-- ===============================

-- ---------- Core Documents ----------

CREATE TABLE documents (
    document_id UUID PRIMARY KEY,
    shipment_id VARCHAR(64) NOT NULL,
    document_type VARCHAR(16) CHECK (document_type IN ('BOL', 'POD')),
    document_state VARCHAR(32) NOT NULL,
    overall_validation_status VARCHAR(32),
    review_required BOOLEAN DEFAULT FALSE,
    auto_close_eligible BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------- Field Definitions ----------

CREATE TABLE kv_field_definitions (
    field_key VARCHAR(64) PRIMARY KEY,
    document_type VARCHAR(16) NOT NULL,
    data_type VARCHAR(32) NOT NULL,
    mandatory BOOLEAN NOT NULL,
    hard_validation BOOLEAN NOT NULL
);

-- ---------- Extracted DOC KVs ----------

CREATE TABLE document_kv (
    document_id UUID NOT NULL,
    field_key VARCHAR(64) NOT NULL,
    doc_value TEXT,
    status VARCHAR(16) CHECK (status IN ('PRESENT', 'MISSING')),
    confidence NUMERIC(3,2),
    PRIMARY KEY (document_id, field_key),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

-- ---------- Comparison Results ----------

CREATE TABLE document_field_comparisons (
    document_id UUID NOT NULL,
    field_key VARCHAR(64) NOT NULL,
    doc_value TEXT,
    master_value TEXT,
    system_value TEXT,
    match_status VARCHAR(16),
    severity VARCHAR(8),
    source_of_truth VARCHAR(16),
    PRIMARY KEY (document_id, field_key)
);

-- ---------- Validation Summary ----------

CREATE TABLE document_validation_summary (
    document_id UUID PRIMARY KEY,
    total_fields INT,
    matched_fields INT,
    hard_failures INT,
    soft_failures INT,
    missing_fields INT,
    kv_completeness NUMERIC(4,3),
    auto_close_eligible BOOLEAN,
    review_required BOOLEAN
);

-- ---------- Audit Log (Append-Only) ----------

CREATE TABLE document_audit_log (
    audit_id UUID PRIMARY KEY,
    document_id UUID,
    event_type VARCHAR(64),
    actor_role VARCHAR(32),
    actor_id VARCHAR(64),
    event_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    before_state JSONB,
    after_state JSONB
);
