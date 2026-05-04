CREATE TABLE registered_agents (
    agent_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'disabled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE agent_api_credentials (
    credential_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES registered_agents(agent_id) ON DELETE RESTRICT,
    api_key_hash TEXT NOT NULL UNIQUE,
    api_key_prefix TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'revoked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ NULL,
    last_used_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_agent_api_credentials_agent_id
    ON agent_api_credentials(agent_id);