from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.config import get_settings
from app.services.document_service import DocumentService
from app.services.index_service import IndexService
from app.rag.pipeline import RagPipeline

settings = get_settings()
app = FastAPI(title=settings.app_name)

# Basic CORS to enable frontend local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

doc_service = DocumentService(settings)
index_service = IndexService(settings)
rag_pipeline = RagPipeline(settings, index_service=index_service)


@app.get("/health")
def health():
    return {"status": "ok", "mode": settings.mode}


@app.post("/ingest")
def ingest(files: List[UploadFile] = File(...)):
    stored = []
    for f in files:
        stored.append(doc_service.store_file(f))
    return {"ingested": stored}


@app.post("/index")
def index(document_ids: List[str] = Form(...)):
    results = []
    for doc_id in document_ids:
        parsed = doc_service.parse_document(doc_id)
        chunks = index_service.chunk_document(parsed)
        embedded = index_service.embed_chunks(chunks)
        index_service.persist_embeddings(embedded)
        results.append({"document_id": doc_id, "chunks_indexed": len(embedded)})
    return {"indexed": results}


@app.post("/query")
def query(question: str = Form(...), top_k: int = Form(4)):
    answer, contexts = rag_pipeline.answer_question(question, top_k=top_k)
    return {"answer": answer, "contexts": contexts}


@app.post("/generate")
def generate(prompt: str = Form(...), top_k: int = Form(4)):
    structured, contexts = rag_pipeline.generate_structured(prompt, top_k=top_k)
    return {"output": structured, "contexts": contexts}
