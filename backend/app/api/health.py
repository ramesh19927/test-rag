"""Health and bootstrap endpoints."""
from fastapi import APIRouter

from app.databricks import delta_tables, vector_search

router = APIRouter(prefix="/health", tags=["health"])


def bootstrap_platform() -> None:
    """Initialize tables and vector index if they do not exist.

    This keeps local and Databricks environments aligned by creating
    necessary metadata structures at startup.
    """
    delta_tables.ensure_all_tables()
    vector_search.ensure_vector_index()


@router.get("/ready")
async def readiness_probe() -> dict[str, str]:
    """Return a simple readiness payload."""
    return {"status": "ok"}
