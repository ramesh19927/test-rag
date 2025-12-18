"""FastAPI entrypoint for the Databricks RAG platform."""
from fastapi import FastAPI

from app.api import health, ingest, query
from app.config import Settings
from app.utils.logging import configure_logging


settings = Settings()
logger = configure_logging(settings.log_level)


def create_app() -> FastAPI:
    """Create the FastAPI app and register routers."""
    app = FastAPI(
        title="Databricks RAG Platform",
        description="Production-ready RAG stack targeting Databricks and local parity.",
        version="0.1.0",
    )
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(query.router)
    return app


app = create_app()


@app.on_event("startup")
async def startup_event() -> None:
    """Lifecycle hook to ensure metadata tables are ready."""
    logger.info("Application startup: initializing tables and vector indices")
    health.bootstrap_platform()
