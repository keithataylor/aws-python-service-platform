"""Shared API dependencies."""

from fastapi import Request
from app.policy.models import AgentPolicyDocument

def get_agent_policy(request: Request) -> AgentPolicyDocument:
  return request.app.state.agent_policy