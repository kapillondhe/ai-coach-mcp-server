import os

from opentelemetry.sdk.resources import Resource
from phoenix.otel import register

from mcp_server.config import get_settings


def setup_telemetry() -> None:

    settings = get_settings()
    if not settings.phoenix_api_key:
        return

    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = settings.phoenix_collector_endpoint

    register(
        project_name=settings.phoenix_project_name,
        api_key=settings.phoenix_api_key,
        resource=Resource.create({"service.name": settings.otel_service_name}),
        batch=True,
    )
