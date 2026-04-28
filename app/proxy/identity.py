"""Agent identity resolution boundary for MCP proxy requests."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResolvedAgentIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1, max_length=100)
    auth_method: str = Field(min_length=1, max_length=50)
    tenant_id: str | None = Field(default=None, min_length=1, max_length=100)
    roles: list[str] = Field(default_factory=list)


def resolve_agent_identity_from_mcp_meta(
    meta: dict[str, Any] | None,
) -> ResolvedAgentIdentity:
    """Resolve agent identity from MCP request metadata.

    This preserves the current behaviour while introducing a stable identity boundary.
    Later adapters can resolve the same shape from API keys, JWTs, or gateway identity.
    """
    if meta:
        agent_id = meta.get("agent_id", "unknown-agent")
    else:
        agent_id = "unknown-agent"

    return ResolvedAgentIdentity(
        agent_id=str(agent_id),
        auth_method="mcp_meta",
    )