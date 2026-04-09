"""Agent action API schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.policy.models import PolicyObligation

AgentDecision = Literal["allow", "deny"]


class InvocationDecisionRequest(BaseModel):
    request_id: str
    agent_id: str
    server_name: str
    tool_name: str
    action: str
    resource: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class InvocationDecisionResponse(BaseModel):
    decision: AgentDecision
    rationale: list[str] = Field(min_length=1)
    obligations: list[PolicyObligation] = Field(default_factory=list)


    