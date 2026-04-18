from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_agent_policy
from app.policy.models import PolicyDocument
from app.main import app, mcp_app

from tests.factories import build_test_policy


@pytest.fixture
def test_policy() -> PolicyDocument:
    return build_test_policy()


@pytest.fixture
def override_agent_policy(test_policy: PolicyDocument):
    def _override_get_agent_policy() -> PolicyDocument:
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
