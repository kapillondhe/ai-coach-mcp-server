from __future__ import annotations

import threading
import uuid
from functools import lru_cache
from typing import Any

from qdrant_client import QdrantClient, models

from mcp_server.config import get_settings

_EMBED_LOCK = threading.Lock()

# Pinned so ingestion and search always embed with the same model — vectors from
# different models aren't comparable. 384-dim, 512-token max sequence length.
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

_CHUNK_ID_NAMESPACE = uuid.UUID("d6e1a7b0-6b1a-4b8a-9c0e-1f2a3b4c5d6e")


def chunk_id(source: str, chunk_index: int) -> str:
    """Deterministic point ID so re-ingesting a source replaces its old chunks instead of duplicating them."""
    return str(uuid.uuid5(_CHUNK_ID_NAMESPACE, f"{source}#{chunk_index}"))


class VectorStore:
    """Thin wrapper around QdrantClient for the coaching knowledge base collection."""

    def __init__(self, client: QdrantClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    def ensure_collection(self) -> None:
        if self._client.collection_exists(self._collection):
            return
        size = self._client.get_embedding_size(EMBEDDING_MODEL)
        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE),
        )
        self._client.create_payload_index(self._collection, field_name="domain", field_schema="keyword")
        self._client.create_payload_index(self._collection, field_name="source", field_schema="keyword")

    def upsert_chunks(self, chunks: list[dict[str, Any]]) -> None:
        """Each chunk: {"text": str, "source": str, "domain": str, "chunk_index": int}."""
        self.ensure_collection()
        points = [
            models.PointStruct(
                id=chunk_id(chunk["source"], chunk["chunk_index"]),
                vector=models.Document(text=chunk["text"], model=EMBEDDING_MODEL),
                payload={"text": chunk["text"], "source": chunk["source"], "domain": chunk["domain"]},
            )
            for chunk in chunks
        ]
        with _EMBED_LOCK:
            self._client.upsert(collection_name=self._collection, points=points)

    def delete_stale_sources(self, current_sources: set[str]) -> None:
        """Remove chunks whose source file no longer exists under knowledge_base/."""
        if not self._client.collection_exists(self._collection):
            return

        existing_sources: set[str] = set()
        offset = None
        while True:
            records, offset = self._client.scroll(
                collection_name=self._collection,
                with_payload=["source"],
                with_vectors=False,
                limit=256,
                offset=offset,
            )
            existing_sources.update(record.payload["source"] for record in records if record.payload)
            if offset is None:
                break

        for source in existing_sources - current_sources:
            self._client.delete(
                collection_name=self._collection,
                points_selector=models.Filter(
                    must=[models.FieldCondition(key="source", match=models.MatchValue(value=source))]
                ),
            )

    def search(
        self,
        query: str,
        domain: str | None,
        top_k: int,
        score_threshold: float,
    ) -> list[dict[str, Any]]:
        self.ensure_collection()
        query_filter = (
            models.Filter(must=[models.FieldCondition(key="domain", match=models.MatchValue(value=domain))])
            if domain
            else None
        )
        with _EMBED_LOCK:
            result = self._client.query_points(
                collection_name=self._collection,
                query=models.Document(text=query, model=EMBEDDING_MODEL),
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold,
            )
        return [
            {
                "text": point.payload["text"],
                "source": point.payload["source"],
                "domain": point.payload["domain"],
                "score": point.score,
            }
            for point in result.points
        ]


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return VectorStore(client, settings.qdrant_collection)
