"""Service responsible for accepting files and staging them into Delta."""
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.databricks import delta_tables
from app.models.document import Document
from app.utils import text_utils


class IngestionService:
    """Handle document ingestion lifecycle."""

    async def ingest_file(self, file: UploadFile) -> str:
        """Persist file to disk, clean content, and write to Delta raw table."""
        contents = await file.read()
        raw_text = contents.decode("utf-8", errors="ignore")
        normalized = text_utils.normalize_text(raw_text)
        doc = Document(
            id=str(uuid.uuid4()),
            name=file.filename,
            source_path=Path(file.filename).as_posix(),
            raw_text=raw_text,
            cleaned_text=normalized,
            metadata={"content_type": file.content_type},
        )
        delta_tables.write_raw_document(doc)
        return doc.id
