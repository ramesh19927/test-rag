"""Service to embed chunks and write them to Delta and Vector Search."""
from __future__ import annotations

from typing import Iterable, List

import mlflow

from app.config import get_settings
from app.databricks import delta_tables, vector_search
from app.models.chunk import Chunk
from app.utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generate embeddings using an MLflow-tracked model."""

    def __init__(self) -> None:
        self.settings = get_settings()
        mlflow.set_experiment(self.settings.experiment_name)

    def embed_chunks(self, chunks: Iterable[Chunk]) -> List[Chunk]:
        """Embed provided chunks and persist embeddings."""
        with mlflow.start_run(run_name="embedding"):
            mlflow.log_param("embedding_model", self.settings.embedding_model)
            enriched_chunks: List[Chunk] = []
            for chunk in chunks:
                # Production would call Databricks Model Serving. We simulate with hash-based vector.
                embedding = vector_search.embed_text(chunk.content, self.settings.embedding_model)
                chunk.embedding = embedding
                enriched_chunks.append(chunk)
            delta_tables.write_embeddings(enriched_chunks)
            vector_search.upsert_embeddings(enriched_chunks)
            mlflow.log_metric("chunks_embedded", len(enriched_chunks))
        return enriched_chunks
