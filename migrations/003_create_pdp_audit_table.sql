CREATE TABLE IF NOT EXISTS pdp_audit (
    id BIGSERIAL PRIMARY KEY,
    request_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    server_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    invocation_action TEXT NOT NULL,
    resource TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('allow', 'deny')),
    rationale TEXT[] NOT NULL,
    policy_version TEXT NOT NULL,
    policy_sha256 TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pdp_audit_request_id
    ON pdp_audit (request_id);