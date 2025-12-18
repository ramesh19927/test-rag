"""Service to chunk normalized documents."""
from app.config import get_settings
from app.databricks import delta_tables
from app.models.chunk import Chunk
from app.models.document import Document
from app.utils import text_utils


class ChunkingService:
    """Break cleaned documents into overlapping chunks and persist them."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Create overlapping chunks and write to Delta."""
        text_chunks = text_utils.chunk_text(
            document.cleaned_text,
            self.settings.chunk_size,
            self.settings.chunk_overlap,
        )
        chunks: list[Chunk] = []
        for idx, content in enumerate(text_chunks):
            chunk = Chunk(
                id=f"{document.id}-{idx}",
                document_id=document.id,
                content=content,
                chunk_index=idx,
                metadata=document.metadata,
            )
            chunks.append(chunk)
        delta_tables.write_chunks(chunks)
        return chunks
