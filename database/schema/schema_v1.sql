-- ============================================================
-- Schema: Logistics Document Validation
-- Version: v1.0
-- Phase: 1 (DDL only)
-- ============================================================

-- ----------------------------
-- 1. Documents
-- ----------------------------
CREATE TABLE documents (
    document_id UUID PRIMARY KEY,
    document_type VARCHAR(10) NOT NULL
        CHECK (document_type IN ('BOL', 'POD')),

    shipment_id VARCHAR(64) NOT NULL,
    related_bol_number VARCHAR(64),

    document_version VARCHAR(20) NOT NULL,
    source_file_name TEXT NOT NULL,

    ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    overall_validation_status VARCHAR(20) NOT NULL
        CHECK (overall_validation_status IN
            ('VALID','EXCEPTION','REJECTED','APPROVED','OVERRIDDEN','CLOSED')),

    auto_close_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    review_required BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_documents_shipment_id
    ON documents (shipment_id);

-- ----------------------------
-- 2. KV Field Definitions (Schema Registry)
-- ----------------------------
CREATE TABLE kv_field_definitions (
    field_key VARCHAR(64) PRIMARY KEY,
    document_type VARCHAR(10) NOT NULL
        CHECK (document_type IN ('BOL','POD')),

    data_type VARCHAR(20) NOT NULL,
    mandatory BOOLEAN NOT NULL,
    hard_validation BOOLEAN NOT NULL,

    description TEXT
);

-- ----------------------------
-- 3. Document Field Comparisons
-- ----------------------------
CREATE TABLE document_field_comparisons (
    comparison_id UUID PRIMARY KEY,
    document_id UUID NOT NULL
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    field_key VARCHAR(64) NOT NULL
        REFERENCES kv_field_definitions(field_key),

    doc_value TEXT,
    master_value TEXT,
    system_value TEXT,

    match_status VARCHAR(20) NOT NULL
        CHECK (match_status IN ('MATCH','MISMATCH','MISSING','DERIVED')),

    severity VARCHAR(10) NOT NULL
        CHECK (severity IN ('HARD','SOFT','INFO')),

    source_of_truth VARCHAR(10) NOT NULL
        CHECK (source_of_truth IN ('DOC','MASTER','SYSTEM')),

    confidence_score NUMERIC(5,2),
    validation_message TEXT
);

CREATE INDEX idx_field_comp_document
    ON document_field_comparisons (document_id);

CREATE INDEX idx_field_comp_field
    ON document_field_comparisons (field_key);

-- ----------------------------
-- 4. Document Validation Summary
-- ----------------------------
CREATE TABLE document_validation_summary (
    document_id UUID PRIMARY KEY
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    total_fields INTEGER NOT NULL,
    matched_fields INTEGER NOT NULL,
    hard_failures INTEGER NOT NULL,
    soft_failures INTEGER NOT NULL,
    missing_fields INTEGER NOT NULL,

    kv_completeness NUMERIC(5,2) NOT NULL,
    validation_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
-- 5. Document Exceptions
-- ----------------------------
CREATE TABLE document_exceptions (
    exception_id UUID PRIMARY KEY,
    document_id UUID NOT NULL
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    field_key VARCHAR(64),
    exception_code VARCHAR(32) NOT NULL,

    severity VARCHAR(10) NOT NULL
        CHECK (severity IN ('HARD','SOFT')),

    exception_description TEXT NOT NULL,

    raised_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_by VARCHAR(64),
    resolved_at TIMESTAMP
);

CREATE INDEX idx_exceptions_document
    ON document_exceptions (document_id);

-- ----------------------------
-- 6. Document Audit Log (Append-only)
-- ----------------------------
CREATE TABLE document_audit_log (
    audit_id UUID PRIMARY KEY,
    document_id UUID NOT NULL
        REFERENCES documents(document_id),

    action VARCHAR(50) NOT NULL,
    actor VARCHAR(64) NOT NULL,

    action_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    before_state JSONB,
    after_state JSONB
);

CREATE INDEX idx_audit_document
    ON document_audit_log (document_id);