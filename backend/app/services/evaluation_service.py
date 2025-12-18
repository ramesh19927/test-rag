"""Evaluate RAG responses for relevance and latency."""
from __future__ import annotations

import time
from typing import Iterable

import mlflow

from app.config import get_settings
from app.models.query import QueryResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)


class EvaluationService:
    """Track evaluation metrics and optionally capture human feedback."""

    def __init__(self) -> None:
        self.settings = get_settings()
        mlflow.set_experiment(self.settings.experiment_name)

    def evaluate(self, responses: Iterable[QueryResponse]) -> dict[str, float]:
        """Compute basic metrics and log them to MLflow."""
        start = time.monotonic()
        scores = [self._score_response(resp) for resp in responses]
        latency_ms = (time.monotonic() - start) * 1000
        avg_score = sum(scores) / max(len(scores), 1)
        with mlflow.start_run(run_name="evaluation"):
            mlflow.log_metric("avg_relevance_score", avg_score)
            mlflow.log_metric("latency_ms", latency_ms)
            mlflow.log_metric("responses_evaluated", len(scores))
        return {"avg_relevance_score": avg_score, "latency_ms": latency_ms}

    @staticmethod
    def _score_response(response: QueryResponse) -> float:
        """Heuristic scoring placeholder; replace with offline eval or crowd feedback."""
        return 0.8 if response.retrieved_chunks else 0.2
