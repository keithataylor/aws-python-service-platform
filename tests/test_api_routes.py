
def test_health_endpoint_returns_ok(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_service_info_returns_service_metadata(client) -> None:
    response = client.get("/api/v1/service-info")

    assert response.status_code == 200
    assert response.json() == {'service': 'AWS Python Service Platform', 'version': '0.1.0'}


def test_echo_endpoint_returns_submitted_text(client) -> None:
    response = client.post("/api/v1/echo", json={"text": "hello"})
    assert response.status_code == 200
    assert response.json() == {"text": "hello"}


def test_echo_rejects_missing_text(client) -> None:
    response = client.post("/api/v1/echo", json={})
    assert response.status_code == 422  


def test_submit_task_accepts_request(client) -> None:
    response = client.post("/api/v1/tasks", json={"name": "demo-task"})
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "submitted"
    assert isinstance(data["task_id"], str)
    assert data["task_id"] != ""


def test_submit_task_reject_empty_name(client) -> None:
    response = client.post("/api/v1/tasks", json={"name": ""})
    assert response.status_code == 422


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
        client, override_agent_policy
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
        client, override_agent_policy
) -> None:
    response = client.post(
        "/api/v1/agent-actions/evaluate",
        json={
            "request_id": "request-123",
            "agent_id": "agent-123",
            "server_name": "server-123",
            "tool_name": "docs_tool",
            "action": "tool.read",
            "resource": "public.docs",
            "parameters": {"document_visibility": "unknown"},
            "context": {},
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "decision": "deny",
        "rationale": ["DEFAULT_DENY"],
        "obligations": [],
    }


def test_evaluate_agent_action_endpoint_returns_allow_for_matching_constraint(
        client, override_agent_policy
) -> None:
    response = client.post(
        "/api/v1/agent-actions/evaluate",
        json={
            "request_id": "request-123",
            "agent_id": "agent-123",
            "server_name": "docs_mcp",
            "tool_name": "docs_tool",
            "action": "tool.read",
            "resource": "public.docs",
            "parameters": {"document_visibility": "public"},
            "context": {"user_role": "reader"},
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "decision": "allow",
        "rationale": ["POLICY_ALLOW_PUBLIC_DOCS_READ"],
        "obligations": [],
    }

