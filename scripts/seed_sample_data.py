"""Seed the platform with sample documents for demos or tests."""
from pathlib import Path

from app.models.document import Document
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService


SAMPLE_TEXT = """Databricks brings together data engineering, data science, and AI on one platform.
The Delta Lake format provides ACID transactions on cloud object storage and is ideal for
storing raw and enriched documents for retrieval-augmented generation."""


def main() -> None:
    """Seed pipeline with a synthetic document to keep notebooks lightweight."""
    ingestion = IngestionService()
    chunking = ChunkingService()
    embedding = EmbeddingService()

    # Simulate ingest without file I/O for ease of use in CI environments.
    doc = Document(
        id="seed-doc",
        name="seed.md",
        source_path=str(Path.cwd() / "seed.md"),
        raw_text=SAMPLE_TEXT,
        cleaned_text=SAMPLE_TEXT.lower(),
        metadata={"seed": True},
    )
    from app.databricks import delta_tables

    delta_tables.write_raw_document(doc)
    delta_tables.write_parsed_document(doc)
    chunks = chunking.chunk_document(doc)
    embedding.embed_chunks(chunks)
    print("Seed data loaded")


if __name__ == "__main__":
    main()
