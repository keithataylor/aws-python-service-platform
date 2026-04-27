"""
Deterministic PDP evaluator for loaded policy documents and invocation requests.
"""

from app.policy.models import PolicyConstraint, PolicyDocument, PolicyRule
from app.schemas.invocation import InvocationDecisionRequest, InvocationDecisionResponse


def _constraint_matches(
    constraint: PolicyConstraint,
    payload: InvocationDecisionRequest,
) -> bool:
    actual_value = payload.decision_context.get(constraint.field)

    if constraint.operator == "equals":
        return actual_value == constraint.value

    if constraint.operator == "in":
        return actual_value in constraint.value

    if constraint.operator == "not_in":
        return actual_value not in constraint.value

    return False


def _rule_matches(
    rule: PolicyRule,
    payload: InvocationDecisionRequest,
) -> bool:
    if rule.when.tool_name != payload.tool_name:     
        return False

    if rule.when.server_name != payload.server_name:
        return False
    
    if rule.when.action != payload.action:
        return False

    if rule.when.resource != payload.resource:
        return False

    return all(
        _constraint_matches(constraint, payload)
        for constraint in rule.when.constraints
    )


def pdp_evaluate_agent_action(
        payload: InvocationDecisionRequest, 
        policy: PolicyDocument
        ) -> InvocationDecisionResponse:  
    """
    Evaluates an agent's tool invocation request against the provided policy document.
    Args:
        payload (InvocationDecisionRequest): The normalized tool invocation request 
        containing details about the agent, tool, action, resource, and decision context.
        policy (PolicyDocument): The policy document containing rules and default decision
        for evaluating the request.
    Returns:
        InvocationDecisionResponse: The decision response containing the decision, rationale,
        and obligations.
    """

    for rule in policy.rules:  
        if _rule_matches(rule, payload):
            return InvocationDecisionResponse(
                decision=rule.then.effect,
                rationale=[rule.then.rationale],
                obligations=rule.then.obligations,
            )
        
    default_rationale = (
        "DEFAULT_DENY"
        if policy.default_decision == "deny"
        else "POLICY_DEFAULT_ALLOW"
    )

    return InvocationDecisionResponse(
        decision=policy.default_decision,
        rationale=[default_rationale],
        obligations=[],
    )