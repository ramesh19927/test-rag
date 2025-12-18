"""Utilities to bridge local and Databricks workspace execution."""
from __future__ import annotations

from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_workspace_client():
    """Placeholder for Databricks SDK client creation.

    In production this would instantiate `WorkspaceClient` to manage assets, clusters,
    and jobs. Here we keep the contract explicit to show where platform integration
    occurs.
    """
    logger.info("Workspace client requested - replace with databricks-sdk in production")
    return None
