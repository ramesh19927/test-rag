"""Document ingestion routes."""
from fastapi import APIRouter, UploadFile

from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingest", tags=["ingest"])
service = IngestionService()


@router.post("/")
async def ingest_document(file: UploadFile) -> dict[str, str]:
    """Ingest a document and push into the Delta raw table."""
    doc_id = await service.ingest_file(file)
    return {"document_id": doc_id}
