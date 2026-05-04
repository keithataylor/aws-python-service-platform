"""Agent identity resolution boundary for MCP proxy requests."""

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field

from app.auth.agent_credentials_repository import get_active_agent_id_for_api_key_hash
from app.auth.credential_hashing import hash_agent_api_key
from app.core.config import get_settings


class ResolvedAgentIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1, max_length=100)
    auth_method: str = Field(min_length=1, max_length=50)
    tenant_id: str | None = Field(default=None, min_length=1, max_length=100)
    roles: list[str] = Field(default_factory=list)


def resolve_agent_identity(*, request: Request) -> ResolvedAgentIdentity:
    """Resolve agent identity from a registered API-key credential."""
    settings = get_settings()
    api_key = request.headers.get("X-Agent-Api-Key")

    if api_key is None:
        return ResolvedAgentIdentity(
            agent_id="unknown-agent",
            auth_method="none",
        )

    api_key_hash = hash_agent_api_key(
        api_key=api_key,
        secret=settings.agent_credential_hash_secret,
    )
    agent_id = get_active_agent_id_for_api_key_hash(api_key_hash)

    if agent_id is None:
        return ResolvedAgentIdentity(
            agent_id="unknown-agent",
            auth_method="none",
        )

    return ResolvedAgentIdentity(
        agent_id=agent_id,
        auth_method="api_key",
    )