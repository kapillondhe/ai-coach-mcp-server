import asyncio

import pytest
from qdrant_client import QdrantClient

from mcp_server.rag.vector_store import VectorStore
from mcp_server.tools import knowledge_base

_PROTEIN_CHUNK = {
    "text": "Protein intake for muscle gain should be 1.6 to 2.2 grams per kilogram of body weight per day.",
    "source": "protein-timing.md",
    "domain": "nutrition",
    "chunk_index": 0,
}
_KNEE_CHUNK = {
    "text": "For a knee injury, substitute back squats with leg press, step-ups, or Bulgarian split squats.",
    "source": "knee-safe-substitutions.md",
    "domain": "exercises",
    "chunk_index": 0,
}


@pytest.fixture
def store() -> VectorStore:
    vector_store = VectorStore(QdrantClient(":memory:"), "test_kb")
    vector_store.upsert_chunks([_PROTEIN_CHUNK, _KNEE_CHUNK])
    return vector_store


def test_search_returns_relevant_chunk(store):
    results = store.search(
        "how much protein should I eat to build muscle", domain=None, top_k=5, score_threshold=0.3
    )
    assert results
    assert results[0]["source"] == "protein-timing.md"


def test_search_respects_domain_filter(store):
    results = store.search("body weight guidance", domain="nutrition", top_k=5, score_threshold=0.0)
    assert results
    assert all(r["domain"] == "nutrition" for r in results)


def test_search_returns_empty_for_unrelated_query(store):
    results = store.search(
        "what's the weather forecast for tomorrow", domain=None, top_k=5, score_threshold=0.6
    )
    assert results == []


def test_reupsert_same_source_replaces_rather_than_duplicates(store):
    store.upsert_chunks(
        [
            {
                "text": "UPDATED: protein needs are 1.6 to 2.2 g/kg for muscle gain.",
                "source": "protein-timing.md",
                "domain": "nutrition",
                "chunk_index": 0,
            }
        ]
    )
    results = store.search("protein for muscle gain", domain=None, top_k=10, score_threshold=0.0)
    protein_matches = [r for r in results if r["source"] == "protein-timing.md"]
    assert len(protein_matches) == 1
    assert "UPDATED" in protein_matches[0]["text"]


def test_search_knowledge_base_tool_returns_matches(monkeypatch, store):
    monkeypatch.setattr(knowledge_base, "get_vector_store", lambda: store)
    results = asyncio.run(knowledge_base.search_knowledge_base("protein for muscle gain"))
    assert results
    assert "source" in results[0]


def test_search_knowledge_base_tool_degrades_gracefully_on_error(monkeypatch):
    class BrokenStore:
        def search(self, *args, **kwargs):
            raise ConnectionError("qdrant unreachable")

    monkeypatch.setattr(knowledge_base, "get_vector_store", lambda: BrokenStore())
    results = asyncio.run(knowledge_base.search_knowledge_base("anything"))
    assert results == []
