"""Agent identity resolution boundary for MCP proxy requests."""

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import get_settings


class ResolvedAgentIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1, max_length=100)
    auth_method: str = Field(min_length=1, max_length=50)
    tenant_id: str | None = Field(default=None, min_length=1, max_length=100)
    roles: list[str] = Field(default_factory=list)


def resolve_agent_identity(*, request: Request) -> ResolvedAgentIdentity:
    """Resolve agent identity from the configured API-key request header."""
    settings = get_settings()
    api_key = request.headers.get("X-Agent-Api-Key")

    if not settings.agent_api_key or api_key != settings.agent_api_key:
        return ResolvedAgentIdentity(
            agent_id="unknown-agent",
            auth_method="none",
        )

    return ResolvedAgentIdentity(
        agent_id=settings.agent_id,
        auth_method="api_key",
    )