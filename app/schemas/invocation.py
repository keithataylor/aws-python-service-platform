"""
Typed PDP invocation and decision response schemas.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.policy.models import PolicyObligation

AgentDecision = Literal["allow", "deny"]


class InvocationDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    agent_id: str
    server_name: str
    tool_name: str
    action: str
    resource: str
    decision_context: dict[str, Any]



class InvocationDecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    decision: AgentDecision
    rationale: list[str] = Field(min_length=1)
    obligations: list[PolicyObligation] = Field(default_factory=list)


    