import pytest

pytestmark = pytest.mark.integration

def test_health_endpoint_returns_ok(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_service_info_returns_service_metadata(client) -> None:
    response = client.get("/api/v1/service-info")

    assert response.status_code == 200
    assert response.json() == {'service': 'AWS Python Service Platform', 'version': '0.1.0'}


def test_evaluate_agent_action_endpoint_returns_default_deny(client) -> None:
    response = client.post(
        "/api/v1/agent-actions/evaluate",
        json={
            "request_id": "request-123",
            "agent_id": "agent-123",
            "server_name": "server-123",
            "tool_name": "crm_tool",
            "action": "tool.call",
            "resource": "crm.contacts",
            "parameters": {},
            "context": {},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "decision": "deny",
        "rationale": ["DEFAULT_DENY"],
        "obligations": [],
    }

def test_evaluate_agent_action_rejects_missing_agent_id(
        client, override_loaded_policy
) -> None:
    response = client.post(
        "/api/v1/agent-actions/evaluate",
        json={
            "request_id": "request-123",
            "server_name": "server-123",
            "tool_name": "crm_tool",
            "action": "tool.call",
            "resource": "crm.contacts",
            "parameters": {},
            "context": {},
        },
    )
    assert response.status_code == 422


def test_evaluate_agent_action_endpoint_returns_deny_for_non_matching_constraint(
        client, override_loaded_policy
) -> None:
    response = client.post(
        "/api/v1/agent-actions/evaluate",
        json={
            "request_id": "request-123",
            "agent_id": "agent-123",
            "server_name": "server-123",
            "tool_name": "docs_tool",
            "action": "document.read",
            "resource": "document",
            "parameters": {"document_id": "doc3"},
            "context": {"document_visibility": "unknown"},
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "decision": "deny",
        "rationale": ["DEFAULT_DENY"],
        "obligations": [],
    }


def test_evaluate_agent_action_endpoint_returns_allow_for_matching_constraint(
        client, override_loaded_policy
) -> None:
    response = client.post(
        "/api/v1/agent-actions/evaluate",
        json={
            "request_id": "request-123",
            "agent_id": "agent-123",
            "server_name": "docs_mcp",
            "tool_name": "docs_tool",
            "action": "document.read",
            "resource": "document",
            "parameters": {"document_id": "doc3"},
            "context": {
                "document_visibility": "public",
                "user_role": "reader"
            },
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "decision": "allow",
        "rationale": ["POLICY_ALLOW_PUBLIC_DOCS_READ"],
        "obligations": [],
    }


def test_health_check_returns_503_when_database_unavailable(client, monkeypatch) -> None:
    monkeypatch.setattr("app.api.routes.check_database_health", lambda: False)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "database connection failed"}

