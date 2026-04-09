"""Shared API dependencies."""

from fastapi import Request
from app.policy.models import PolicyDocument

def get_agent_policy(request: Request) -> PolicyDocument:
  return request.app.state.agent_policy