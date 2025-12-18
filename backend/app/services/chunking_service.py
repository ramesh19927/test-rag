"""Service to chunk normalized documents."""
import mlflow

from app.config import get_settings
from app.databricks import delta_tables
from app.databricks import mlflow_tracking
from app.models.chunk import Chunk
from app.models.document import Document
from app.utils import text_utils


class ChunkingService:
    """Break cleaned documents into overlapping chunks and persist them."""

    def __init__(self) -> None:
        self.settings = get_settings()
        mlflow_tracking.configure_experiment()

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
        with mlflow.start_run(run_name="chunking"):
            mlflow.log_params(
                {"chunk_size": self.settings.chunk_size, "chunk_overlap": self.settings.chunk_overlap}
            )
            delta_tables.write_chunks(chunks)
            mlflow.log_metric("chunks_created", len(chunks))
        return chunks
