from fastmcp import FastMCP

from mcp_server.auth import SharedSecretVerifier
from mcp_server.config import get_settings
from mcp_server.telemetry import setup_telemetry
from mcp_server.tools.knowledge_base import search_knowledge_base
from mcp_server.tools.nutrition import calculate_protein_intake
from mcp_server.tools.zones import (
    calculate_heart_rate_zones,
    calculate_power_zones,
    calculate_swim_pace_zones,
)


def create_server() -> FastMCP:
    settings = get_settings()
    auth = SharedSecretVerifier(settings.mcp_auth_token) if settings.mcp_auth_token else None

    server = FastMCP("ai-coach-tools", auth=auth)
    server.tool(calculate_protein_intake)
    server.tool(search_knowledge_base)
    server.tool(calculate_heart_rate_zones)
    server.tool(calculate_power_zones)
    server.tool(calculate_swim_pace_zones)
    return server


mcp = create_server()


def main() -> None:
    settings = get_settings()
    setup_telemetry()
    mcp.run(transport="streamable-http", host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()
