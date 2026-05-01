import pytest
from starlette.requests import Request

from app.core.config import get_settings
from app.proxy.identity import resolve_agent_identity

pytestmark = pytest.mark.unit


def test_resolve_agent_identity_from_api_key(monkeypatch):
    # valid API key resolves configured agent_id
    settings = get_settings()
    monkeypatch.setattr(settings, "agent_api_key", "test-api-key")
    monkeypatch.setattr(settings, "agent_id", "configured-agent")

    request = Request(
        scope={
            "type": "http", 
            "headers": [(b"x-agent-api-key", b"test-api-key")]
        }
    )
    
    result = resolve_agent_identity(request=request)
    
    assert result.agent_id == "configured-agent"
    assert result.auth_method == "api_key"


def test_resolve_agent_identity_from_api_key_invalid(monkeypatch):
    # invalid API key falls back to unknown-agent
    settings = get_settings()
    monkeypatch.setattr(settings, "agent_api_key", "test-api-key")

    request = Request(
        scope={
            "type": "http", 
            "headers": [(b"x-agent-api-key", b"invalid-api-key")]
        }
    )
    
    result = resolve_agent_identity(request=request)
    
    assert result.agent_id == "unknown-agent"
    assert result.auth_method == "none"


def test_resolve_agent_identity_no_api_key(monkeypatch):
    # no API key returns unknown-agent
    settings = get_settings()
    monkeypatch.setattr(settings, "agent_api_key", "test-api-key")

    request = Request(
        scope={
            "type": "http", 
            "headers": []
        }
    )
    
    result = resolve_agent_identity(request=request)
    
    assert result.agent_id == "unknown-agent"
    assert result.auth_method == "none"
