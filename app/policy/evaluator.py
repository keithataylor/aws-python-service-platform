"""Agent policy decision service."""

from app.schemas.agent_action import AgentActionDecisionResponse, AgentActionRequest
from app.policy.models import AgentPolicyRule, PolicyConstraint, AgentPolicyDocument


def _constraint_matches(
    constraint: PolicyConstraint,
    parameters: dict[str, object],
) -> bool:
    actual_value = parameters.get(constraint.parameter)

    if constraint.operator == "equals":
        return actual_value == constraint.value

    if constraint.operator == "in":
        return actual_value in constraint.value

    if constraint.operator == "not_in":
        return actual_value not in constraint.value

    return False


def _rule_matches(
    rule: AgentPolicyRule,
    payload: AgentActionRequest,
) -> bool:
    if rule.tool_name != payload.tool_name:
        return False

    if rule.action != payload.action:
        return False

    if rule.resource != payload.resource:
        return False

    return all(
        _constraint_matches(constraint, payload.parameters)
        for constraint in rule.constraints
    )


def evaluate_agent_action(
        payload: AgentActionRequest, 
        policy: AgentPolicyDocument
        ) -> AgentActionDecisionResponse:  

    for rule in policy.rules:
        if _rule_matches(rule, payload):
            return AgentActionDecisionResponse(
                decision=rule.effect,
                rationale=[rule.rationale],
                obligations=rule.obligations,
            )

    default_rationale = (
        "DEFAULT_DENY"
        if policy.default_decision == "deny"
        else "POLICY_DEFAULT_ALLOW"
    )

    return AgentActionDecisionResponse(
        decision=policy.default_decision,
        rationale=[default_rationale],
        obligations=[],
    )