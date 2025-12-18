"""Generate grounded responses using retrieved context."""
from typing import List

import mlflow

from app.config import get_settings
from app.models.query import QueryRequest, QueryResponse
from app.databricks import mlflow_tracking
from app.services.retrieval_service import RetrievalService
from app.utils.logging import get_logger
from app.utils.text_utils import format_prompt

logger = get_logger(__name__)


class GenerationService:
    """Orchestrate retrieval, prompt construction, and generation."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.retrieval = RetrievalService()
        mlflow_tracking.configure_experiment()

    async def generate_response(self, request: QueryRequest) -> QueryResponse:
        """Generate a RAG response and log parameters to MLflow."""
        with mlflow.start_run(run_name="generation"):
            mlflow.log_params(
                {
                    "llm_model": self.settings.llm_model,
                    "prompt_version": "rag_prompt_v1",
                    "top_k": request.top_k,
                }
            )
            retrieved = self.retrieval.retrieve(request.query, k=request.top_k)
            prompt = format_prompt(request.query, [chunk.content for chunk in retrieved])
            # Mock LLM response; in production call Databricks Model Serving endpoint.
            answer = f"Simulated answer to '{request.query}' grounded on {len(retrieved)} chunks."
            mlflow.log_metric("retrieved_chunks", len(retrieved))
            return QueryResponse(
                answer=answer,
                retrieved_chunks=[chunk.content for chunk in retrieved],
                prompt=prompt,
            )
