# AI Coach — MCP Server

Standalone MCP server exposing fitness-coaching tools (log/lookup workouts) over
streamable HTTP. Consumed by the [AI Coach backend](https://github.com/kapillondhe/ai-coach-backend)'s
Pydantic AI coach agent as a tool provider, but has no dependency on that repo — any
MCP client can talk to it.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
source .venv/bin/activate
python -m mcp_server
```

Serves streamable HTTP on `MCP_PORT` (default `8100`) at `/mcp`.

Set `MCP_AUTH_TOKEN` in `.env` to require a bearer token from callers; unset for local
dev with a single trusted caller.

To exercise the tools directly, independent of any client, use the MCP Inspector:

```bash
PYTHONPATH=. fastmcp dev mcp_server/server.py
```

## Test

```bash
source .venv/bin/activate
pytest
```

## Layout

```
mcp_server/
  server.py      FastMCP instance + tool registration
  auth.py        shared-secret bearer token verifier
  config.py      env-driven settings (pydantic-settings)
  tools/         one module per tool group (plain async functions)
  data/          placeholder in-memory persistence
tests/
```
