from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_agent_policy
from app.policy.models import AgentPolicyDocument
from tests.factories import build_test_policy

# Adjust this import to match where your FastAPI app actually lives.
# If main.py is repo root, use: from main import app
from app.main import app


@pytest.fixture
def test_policy() -> AgentPolicyDocument:
    return build_test_policy()


@pytest.fixture
def override_agent_policy(test_policy: AgentPolicyDocument):
    def _override_get_agent_policy() -> AgentPolicyDocument:
        return test_policy

    app.dependency_overrides[get_agent_policy] = _override_get_agent_policy
    try:
        yield test_policy
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client