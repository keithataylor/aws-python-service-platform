from collections.abc import Iterator

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_agent_policy
from app.policy.models import PolicyDocument
from app.main import app
from app.core.config import get_settings
from app.db.connection import get_db_connection

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
def client(use_test_db, seed_test_documents):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def use_test_db(monkeypatch) -> Iterator[None]:
    settings = get_settings()
    monkeypatch.setenv("DB_NAME", settings.test_db_name)
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()


@pytest.fixture
def seed_test_documents(use_test_db) -> None:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM documents;")
            cursor.execute(
                """
                INSERT INTO documents (
                    document_id,
                    title,
                    summary,
                    body,
                    document_visibility
                ) VALUES
                    ('test_doc_public_1', 'Test Document 1', 'Public test summary', 'Public test body', 'public'),
                    ('test_doc_private_1', 'Test Document 2', 'Private test summary', 'Private test body', 'private')
                """
            )


