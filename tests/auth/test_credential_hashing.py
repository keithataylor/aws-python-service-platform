import pytest

from app.auth.credential_hashing import hash_agent_api_key

pytestmark = pytest.mark.unit

def test_hash_agent_api_key_is_deterministic() -> None:
    api_key = "test-api-key"
    secret = "test-secret-with-more-than-32-chars"

    first_hash = hash_agent_api_key(api_key=api_key, secret=secret)
    second_hash = hash_agent_api_key(api_key=api_key, secret=secret)

    assert first_hash == second_hash


def test_hash_agent_api_key_changes_when_secret_changes() -> None:
    api_key = "test-api-key"

    first_hash = hash_agent_api_key(
        api_key=api_key,
        secret="first-test-secret-with-more-than-32-chars",
    )
    second_hash = hash_agent_api_key(
        api_key=api_key,
        secret="second-test-secret-with-more-than-32-chars",
    )

    assert first_hash != second_hash


def test_hash_agent_api_key_changes_when_api_key_changes() -> None:
    secret = "test-secret-with-more-than-32-chars"

    first_hash = hash_agent_api_key(api_key="first-api-key", secret=secret)
    second_hash = hash_agent_api_key(api_key="second-api-key", secret=secret)

    assert first_hash != second_hash