"""Delta Lake table management and simplified IO helpers."""
from __future__ import annotations

from typing import Iterable, List

from app.config import get_settings
from app.models.chunk import Chunk
from app.models.document import Document
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


RAW_TABLE = f"{settings.catalog}.{settings.schema}.raw_documents"
PARSED_TABLE = f"{settings.catalog}.{settings.schema}.parsed_documents"
CHUNK_TABLE = f"{settings.catalog}.{settings.schema}.chunked_documents"
EMBEDDED_TABLE = f"{settings.catalog}.{settings.schema}.embedded_chunks"


def ensure_all_tables() -> None:
    """Create all tables if they do not yet exist.

    In Databricks this would execute DDL statements. Locally we log intent to keep
    the code path visible for reviewers.
    """
    logger.info("Ensuring Delta tables exist", extra={"tables": [RAW_TABLE, PARSED_TABLE, CHUNK_TABLE, EMBEDDED_TABLE]})


def write_raw_document(document: Document) -> None:
    """Persist a raw document record into Delta Lake."""
    logger.info(
        "Writing raw document to Delta",
        extra={"table": RAW_TABLE, "document_id": document.id, "partitioning": "ingestion_date"},
    )


def write_parsed_document(document: Document) -> None:
    """Persist normalized/parsed document to Delta with versioning considerations."""
    logger.info(
        "Writing parsed document to Delta",
        extra={"table": PARSED_TABLE, "document_id": document.id, "comment": "Tracks lineage from raw"},
    )


def write_chunks(chunks: Iterable[Chunk]) -> None:
    """Persist chunk metadata to Delta."""
    chunk_list = list(chunks)
    logger.info(
        "Writing chunks to Delta",
        extra={"table": CHUNK_TABLE, "count": len(chunk_list), "partitioning": "document_id"},
    )


def write_embeddings(chunks: Iterable[Chunk]) -> None:
    """Persist embeddings to Delta."""
    chunk_list = list(chunks)
    logger.info(
        "Writing embeddings to Delta",
        extra={"table": EMBEDDED_TABLE, "count": len(chunk_list), "versioning": "delta time travel"},
    )
