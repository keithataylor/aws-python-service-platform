"""Policy configuration schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field


PolicyEffect = Literal["allow", "deny"]
PolicyDecision = Literal["allow", "deny"]
ConstraintOperator = Literal["equals", "in", "not_in"]
SourceType = Literal["parameters", "context"]


class PolicyConstraint(BaseModel):
    source: SourceType
    field: str = Field(min_length=1, max_length=100)
    operator: ConstraintOperator
    value: Any


class PolicyObligation(BaseModel):
    obligation_type: str = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)


class PolicyWhen(BaseModel):
    server_name: str | None = None
    tool_name: str
    action: str
    resource: str
    constraints: list[PolicyConstraint] = Field(default_factory=list)

class PolicyThen(BaseModel):
    effect: PolicyEffect
    rationale: str
    obligations: list[PolicyObligation] = Field(default_factory=list)


class PolicyRuleMeta(BaseModel):
    description: str | None = None


class PolicyRule(BaseModel):
    rule_id: str = Field(min_length=1, max_length=100)
    when: PolicyWhen
    then: PolicyThen
    meta: PolicyRuleMeta | None = None


class PolicyDocument(BaseModel):
    version: str = Field(min_length=1, max_length=20)
    default_decision: PolicyDecision
    rules: list[PolicyRule] = Field(default_factory=list)

