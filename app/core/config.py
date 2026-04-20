   
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


SERVICE_NAME = "AWS Python Service Platform"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_FILE = BASE_DIR / "app" / "policies" / "agent_policy.yaml"


class Settings(BaseSettings):
    db_host: str = Field(validation_alias="DB_HOST")
    db_port: int = Field(validation_alias="DB_PORT")
    db_name: str = Field(validation_alias="DB_NAME")
    test_db_name: str = Field(validation_alias="TEST_DB_NAME")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
