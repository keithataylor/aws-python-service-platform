
from app.db.connection import get_db_connection


def test_health_check_returns_503_when_database_unavailable(client, monkeypatch) -> None:
    monkeypatch.setattr("app.api.routes.check_database_health", lambda: False)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "database connection failed"}

    