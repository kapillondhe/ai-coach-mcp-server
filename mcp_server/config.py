from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8100

    # Shared-secret bearer token other services must send to call this server.
    # Unset (the default) disables auth entirely - fine for local dev with a single trusted caller.
    mcp_auth_token: str | None = None

    # Arize Phoenix (Cloud) tracing. Unset phoenix_api_key disables telemetry entirely.
    phoenix_api_key: str | None = None
    phoenix_collector_endpoint: str = "https://app.phoenix.arize.com"
    phoenix_project_name: str = "ai-coach"
    otel_service_name: str = "ai-coach-mcp-server"


@lru_cache
def get_settings() -> Settings:
    return Settings()
