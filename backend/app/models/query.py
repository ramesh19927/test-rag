"""Models used by the query API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class QueryRequest:
    """Incoming query payload."""

    query: str
    top_k: int = 5


@dataclass
class QueryResponse:
    """Response structure for the RAG pipeline."""

    answer: str
    retrieved_chunks: List[str] = field(default_factory=list)
    prompt: str | None = None
