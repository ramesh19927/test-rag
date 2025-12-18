"""Vector Search abstraction with Databricks-first design and local fallback."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List

from app.config import get_settings
from app.models.chunk import Chunk
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class VectorHit:
    """Lightweight representation of a search hit."""

    chunk: Chunk
    score: float


def ensure_vector_index() -> None:
    """Create vector index if missing.

    On Databricks this would call the Vector Search API to create or sync an index.
    Locally we only log the intent so the call graph remains explicit for reviewers.
    """
    logger.info(
        "Ensuring vector search index exists",
        extra={"index_name": settings.vector_index_name, "backing_table": "embedded_chunks"},
    )


def embed_text(text: str, model: str) -> list[float]:
    """Mock embedding function using deterministic hashing for parity tests."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [float(b) / 255.0 for b in digest[:64]]


def upsert_embeddings(chunks: List[Chunk]) -> None:
    """Simulate upserting embeddings into Databricks Vector Search or FAISS."""
    logger.info(
        "Upserting embeddings into vector index",
        extra={"index": settings.vector_index_name, "count": len(chunks)},
    )


def search(query: str, k: int = 5) -> List[Chunk]:
    """Perform vector similarity search.

    This mock implementation returns synthetic chunks while preserving the API shape
    expected from Databricks Vector Search. When running on Databricks, swap this
    logic for calls to the native client.
    """
    embedding = embed_text(query, settings.embedding_model)
    hits: List[Chunk] = []
    for idx in range(k):
        chunk = Chunk(
            id=f"synthetic-{idx}",
            document_id="synthetic",
            content=f"Relevant passage {idx} for query: {query}",
            chunk_index=idx,
            metadata={"synthetic": True},
            embedding=embedding,
        )
        hits.append(chunk)
    return hits
