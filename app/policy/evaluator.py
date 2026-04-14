"""Agent policy decision service."""

from app.schemas.invocation import InvocationDecisionRequest, InvocationDecisionResponse
from app.policy.models import PolicyRule, PolicyConstraint, PolicyDocument


def _constraint_matches(
    constraint: PolicyConstraint,
    payload: InvocationDecisionRequest,
) -> bool:
    
    if constraint.source == "parameters":
        actual_value = payload.parameters.get(constraint.field)
    elif constraint.source == "context":
        actual_value = payload.context.get(constraint.field)  

        

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
        print(f"Action does not match: expected={rule.when.action}, actual={payload.action}")
        return False

    if rule.when.resource != payload.resource:
        print(f"Resource does not match: expected={rule.when.resource}, actual={payload.resource}")
        return False

    return all(
        _constraint_matches(constraint, payload)
        for constraint in rule.when.constraints
    )


def pdp_evaluate_agent_action(
        payload: InvocationDecisionRequest, 
        policy: PolicyDocument
        ) -> InvocationDecisionResponse:  

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