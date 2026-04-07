"""Agent action API schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.policy import PolicyObligation

AgentDecision = Literal["allow", "deny"]


class AgentActionRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=100)
    tool_name: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    resource: str = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)


class AgentActionDecisionResponse(BaseModel):
    decision: AgentDecision
    rationale: list[str] = Field(min_length=1)
    obligations: list[PolicyObligation] = Field(default_factory=list)


    