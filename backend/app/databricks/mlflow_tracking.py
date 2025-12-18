"""Utilities for MLflow tracking aligned with Databricks experiments."""
from __future__ import annotations

import mlflow

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def configure_experiment() -> None:
    """Ensure MLflow is configured for Databricks or local execution."""
    mlflow.set_tracking_uri(settings.databricks_host)
    mlflow.set_experiment(settings.experiment_name)
    logger.info(
        "Configured MLflow tracking",
        extra={"tracking_uri": settings.databricks_host, "experiment": settings.experiment_name},
    )


def log_prompt_version(prompt_name: str, version: str) -> None:
    """Capture prompt lineage alongside model metadata."""
    mlflow.log_param(f"prompt_{prompt_name}_version", version)
