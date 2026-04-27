"""
Shared API dependencies.
"""

from starlette.requests import Request

from app.policy.models import LoadedPolicy, PolicyDocument


def get_agent_policy(request: Request) -> PolicyDocument:
    return get_loaded_policy(request).document


def get_loaded_policy(request: Request) -> LoadedPolicy:
    return request.app.state.loaded_policy


