# Databricks-Native Document Intelligence Platform

An end-to-end Retrieval-Augmented Generation (RAG) system for unstructured documents. The design runs locally for development and maps cleanly onto Databricks for scale, governance, and production reliability.

## What this system does
- Ingest PDFs, DOCX, and text files via a FastAPI backend and simple web UI.
- Parse, chunk, embed, and store text with Databricks-friendly data models (Delta tables + Vector Search).
- Expose endpoints for question answering and structured generation (e.g., SoW-style summaries) over governed content.
- Run locally with filesystem/SQLite for fast iteration; flip a config flag to use Databricks storage and Vector Search.

## Why Databricks
- **Delta as source of truth**: raw, parsed, chunk, and embedding tables mirror data-quality and lineage expectations.
- **Vector Search**: operational similarity search built on governed Delta tables.
- **MLflow**: capture prompt versions and model usage for audits and experiments.
- **Unified platform**: notebooks for batch ingestion, jobs for scheduled indexing, model serving for low-latency RAG.

## High-level architecture
- **Backend (FastAPI)**: `/ingest`, `/index`, `/query`, `/generate`, `/health` endpoints. Config-driven to swap between local storage and Databricks tables.
- **RAG core**: parsers ➜ chunker ➜ embedding client (OpenAI by default; pluggable) ➜ vector search ➜ generator.
- **Frontend**: minimal Vite app to upload files, run queries, and view retrieved context snippets.
- **Databricks assets**: SQL schemas for Delta tables, Vector Search helper script, notebook placeholder for jobs.

```
┌──────────────┐     ┌────────────────┐     ┌─────────────┐     ┌───────────────┐
│   Frontend   │ --> │    FastAPI     │ --> │  Delta/VS   │ --> │ Generation     │
│ (upload/QA)  │     │ (services)     │     │ (search)    │     │ (LLM/MLflow)   │
└──────────────┘     └────────────────┘     └─────────────┘     └───────────────┘
```

## How RAG works here
1. **Ingest**: files saved to raw storage (local disk or UC/DBFS) and registered in `raw_documents` Delta table.
2. **Parse**: text extraction stored in `parsed_documents`.
3. **Chunk**: deterministic splitter writes `text_chunks` rows.
4. **Embed**: embeddings persisted in `embeddings` Delta table; Vector Search index sits over this table.
5. **Retrieve + Generate**: top chunks retrieved for a query; prompts built with context and sent to OpenAI or Databricks FM. MLflow should log prompt/model versions for reproducibility.

## Running locally
1. Copy `.env.example` to `.env` and adjust as needed (OpenAI key optional for offline mode).
2. Build and start services:
   - `docker-compose up --build`
   - Backend available at `http://localhost:8000`, frontend at `http://localhost:5173`.
3. Workflow in UI:
   - Upload documents → note returned `doc_id`s.
   - Index by entering comma-separated IDs.
   - Ask questions or request structured outputs; retrieved chunks are displayed.

### Local data layout
- `./.data/raw`: uploaded files.
- `./.data/parsed`: extracted text.
- `./.data/chunks`: chunk manifests per document.
- `./.data/embeddings.jsonl`: append-only embedding store (mirrors Delta table contract).

## Deploying on Databricks
1. Run `databricks/schemas.sql` in a SQL warehouse to create Delta tables in Unity Catalog.
2. Use `databricks/vector_index.py` (or UI) to sync the `embeddings` table into Vector Search.
3. Configure environment for the backend:
   - `MODE=databricks`
   - `DATABASE_URL` pointing to UC or a JDBC/SQL Warehouse endpoint.
   - Storage paths (DBFS/volumes) for raw and parsed assets.
4. Deploy the FastAPI service on Databricks (model serving or container services). Wire MLflow tracking for prompt/model lineage.
5. Batch ingestion or re-indexing can be orchestrated with Databricks Jobs/Workflows using notebooks under `databricks/notebooks`.

## Trade-offs and future extensions
- **Embeddings**: local deterministic vectors avoid network calls; swap to OpenAI or Databricks FMs by providing credentials. Future work: batching, caching, and multilingual models.
- **Storage**: JSONL simulates Delta locally; production should use Auto Loader and Delta Live Tables for scalability and data quality.
- **Retrieval**: cosine via Vector Search in Databricks; locally uses dense dot-product over in-memory vectors. Future: hybrid search and metadata filters.
- **Generation**: simple prompt builder today; extend with guardrails, evaluation harnesses, and MLflow prompt/version tracking.
- **Security**: add authN/Z, PII scrubbing, and secret management via Databricks secrets scopes.

## Repository layout
See `databricks-ai-platform/` for the full codebase. Key entrypoints:
- `backend/app/main.py`: FastAPI wiring and endpoints.
- `backend/app/services/*`: ingestion and indexing services.
- `backend/app/rag/*`: parsing, chunking, embedding, and generation utilities.
- `frontend/index.html` + `frontend/src/main.js`: minimal client.
- `databricks/*`: deployment artifacts.
