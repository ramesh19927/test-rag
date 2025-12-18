"""Retrieve top-k chunks using Databricks Vector Search with local fallback."""
from typing import List

from app.config import get_settings
from app.databricks import vector_search
from app.models.chunk import Chunk


class RetrievalService:
    """Abstract retrieval to allow Databricks and local parity."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def retrieve(self, query: str, k: int = 5) -> List[Chunk]:
        """Retrieve top-k chunks for a user query."""
        return vector_search.search(query, k=k)
