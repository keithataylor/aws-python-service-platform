"""
Typed policy document models for PDP rule evaluation.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PolicyEffect = Literal["allow", "deny"]
PolicyDecision = Literal["allow", "deny"]
ConstraintOperator = Literal["equals", "in", "not_in"]


class PolicyConstraint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1, max_length=100)
    operator: ConstraintOperator
    value: Any


class PolicyObligation(BaseModel):
    obligation_type: str = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)


class PolicyWhen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    server_name: str | None = None
    tool_name: str
    action: str
    resource: str
    constraints: list[PolicyConstraint] = Field(default_factory=list)

class PolicyThen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effect: PolicyEffect
    rationale: str
    obligations: list[PolicyObligation] = Field(default_factory=list)


class PolicyRuleMeta(BaseModel):
    description: str | None = None


class PolicyRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(min_length=1, max_length=100)
    when: PolicyWhen
    then: PolicyThen
    meta: PolicyRuleMeta | None = None


class PolicyDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(min_length=1, max_length=20)
    default_decision: PolicyDecision
    rules: list[PolicyRule] = Field(default_factory=list)


class LoadedPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    document: PolicyDocument
    policy_sha256: str
    

