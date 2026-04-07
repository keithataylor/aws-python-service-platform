"""Policy configuration schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field


PolicyEffect = Literal["allow", "deny"]
PolicyDecision = Literal["allow", "deny"]
ConstraintOperator = Literal["equals", "in", "not_in"]


class PolicyConstraint(BaseModel):
    parameter: str = Field(min_length=1, max_length=100)
    operator: ConstraintOperator
    value: Any


class PolicyObligation(BaseModel):
    obligation_type: str = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)


class AgentPolicyRuleMeta(BaseModel):
    description: str | None = None


class AgentPolicyRule(BaseModel):
    rule_id: str = Field(min_length=1, max_length=100)
    effect: PolicyEffect
    tool_name: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    resource: str = Field(min_length=1, max_length=100)
    rationale: str = Field(min_length=1, max_length=100)
    meta: AgentPolicyRuleMeta | None = None
    constraints: list[PolicyConstraint] = Field(default_factory=list)
    obligations: list[PolicyObligation] = Field(default_factory=list)


class AgentPolicyDocument(BaseModel):
    version: str = Field(min_length=1, max_length=20)
    default_decision: PolicyDecision
    rules: list[AgentPolicyRule] = Field(default_factory=list)