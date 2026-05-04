import pytest
from starlette.requests import Request

from app.proxy.identity import resolve_agent_identity

pytestmark = pytest.mark.unit


def test_resolve_agent_identity_returns_authenticated_identity_for_resolved_api_key(
    monkeypatch
) -> None:
    request = Request(
        scope={
            "type": "http", 
            "headers": [(b"x-agent-api-key", b"test-api-key")]
        }
    )

    monkeypatch.setattr(
        "app.proxy.identity.get_active_agent_id_for_api_key_hash",
        lambda api_key_hash: "registered-agent",
    )

    result = resolve_agent_identity(request=request)
    
    assert result.agent_id == "registered-agent"
    assert result.auth_method == "api_key"


def test_resolve_agent_identity_returns_unknown_identity_for_invalid_api_key() -> None:
    request = Request(
        scope={
            "type": "http", 
            "headers": [(b"x-agent-api-key", b"invalid-api-key")]
        }
    )
    
    result = resolve_agent_identity(request=request)
    
    assert result.agent_id == "unknown-agent"
    assert result.auth_method == "none"


def test_resolve_agent_identity_no_api_key() -> None:
    request = Request(
        scope={
            "type": "http", 
            "headers": []
        }
    )
    
    result = resolve_agent_identity(request=request)
    
    assert result.agent_id == "unknown-agent"
    assert result.auth_method == "none"
