"""Query endpoint for retrieval and generation."""
from fastapi import APIRouter

from app.models.query import QueryRequest, QueryResponse
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/query", tags=["query"])
generation_service = GenerationService()


@router.post("/")
async def run_query(payload: QueryRequest) -> QueryResponse:
    """Execute a full RAG flow given a user query."""
    return await generation_service.generate_response(payload)
