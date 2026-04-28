"""
Runtime configuration loaded from environment variables.
"""   

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_NAME = "AWS Python Service Platform"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_FILE = BASE_DIR / "app" / "policies" / "agent_policy.yaml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = Field(validation_alias="DB_HOST")
    db_port: int = Field(validation_alias="DB_PORT")
    db_name: str = Field(validation_alias="DB_NAME")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    test_db_name: str = Field(validation_alias="TEST_DB_NAME")
    
    agent_api_key: str | None = Field(default=None, validation_alias="AGENT_API_KEY")
    agent_id: str = Field(default="local-dev-agent", validation_alias="AGENT_ID")



@lru_cache
def get_settings() -> Settings:
    return Settings()

