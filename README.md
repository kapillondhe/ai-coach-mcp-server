# AI Coach — MCP Server

Standalone MCP server exposing fitness-coaching tools over
streamable HTTP. Consumed by the [AI Coach backend](https://github.com/kapillondhe/ai-coach-backend)'s
Pydantic AI coach agent as a tool provider, but has no dependency on that repo — any
MCP client can talk to it.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Local Qdrant, needed by the knowledge-base search tool (mcp_server/rag/)
docker compose up -d

# Ingest knowledge_base/*.md into Qdrant; re-run whenever that content changes
python -m scripts.ingest_knowledge_base
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
  tools/         one module per tool group (plain async functions):
                   nutrition.py       - calculate_protein_intake
                   knowledge_base.py  - search_knowledge_base (RAG over Qdrant)
  rag/           VectorStore wrapper around QdrantClient (mcp_server/rag/vector_store.py)
knowledge_base/  curated .md source content for the RAG tool, one file per topic,
                 grouped by domain (nutrition/, exercises/, training/, physiotherapy/)
scripts/         ingest_knowledge_base.py - chunks knowledge_base/ into Qdrant
tests/
```

Current tools exposed: `calculate_protein_intake` (pure sports-nutrition math) and
`search_knowledge_base` (semantic search over the curated knowledge base, embedded
locally via fastembed — no external embedding API/key needed).
