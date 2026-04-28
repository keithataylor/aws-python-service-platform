"""Agent identity resolution boundary for MCP proxy requests."""

from typing import Any

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import get_settings


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
        return ResolvedAgentIdentity(
            agent_id="unknown-agent",
            auth_method="none",
        )

    return ResolvedAgentIdentity(
        agent_id=str(agent_id),
        auth_method="mcp_meta",
    )


def resolve_agent_identity_from_api_key(api_key: str | None) -> ResolvedAgentIdentity:
    """Resolve agent identity from a configured API key."""
    settings = get_settings()

    if not settings.agent_api_key:
        return ResolvedAgentIdentity(
            agent_id="unknown-agent",
            auth_method="none",
        )

    if api_key != settings.agent_api_key:
        return ResolvedAgentIdentity(
            agent_id="unknown-agent",
            auth_method="invalid_api_key",
        )

    return ResolvedAgentIdentity(
        agent_id=settings.agent_id,
        auth_method="api_key",
    )


def resolve_agent_identity(
    *,
    request: Request,
    meta: dict[str, Any] | None,
) -> ResolvedAgentIdentity:
    """Resolve agent identity from the current request and MCP metadata."""
    api_key_identity = resolve_agent_identity_from_api_key(
        request.headers.get("X-Agent-Api-Key")
    )

    if api_key_identity.agent_id != "unknown-agent":
        return api_key_identity

    return resolve_agent_identity_from_mcp_meta(meta)