# Databricks RAG Platform

An enterprise-ready retrieval augmented generation (RAG) platform that runs consistently on Databricks and on a developer laptop. The system ingests unstructured content, stores curated lineage in Delta Lake, indexes embeddings with Databricks Vector Search (with FAISS-like local fallback), and tracks every model/prompt decision in MLflow. This repository is structured for principal-engineer scrutiny rather than a toy demo.

## Why Databricks?
- **Unified storage and compute** via Delta Lake and Unity Catalog simplify raw-to-curated lineage, auditing, and time travel.
- **Vector Search** provides managed ANN indexing directly on Delta-backed tables, removing bespoke infra.
- **MLflow** is native for experiment tracking, model registry, and prompt governance across jobs and serving endpoints.
- **Jobs + Model Serving** give a single control plane for scheduled pipelines and low-latency inference.

## Architecture
```
databricks-rag-platform/
├── backend/                    # FastAPI service for ingestion, query, evaluation
│   ├── app/
│   │   ├── main.py             # Entrypoint wiring routers
│   │   ├── config.py           # Shared settings for local + Databricks
│   │   ├── api/                # HTTP routes for ingest/query/health
│   │   ├── services/           # Ingestion, chunking, embedding, retrieval, generation, evaluation
│   │   ├── databricks/         # Delta, Vector Search, MLflow, workspace utilities
│   │   ├── models/             # Pydantic/dataclass-style payloads
│   │   ├── prompts/            # Prompt assets tracked via MLflow
│   │   └── utils/              # Logging, text processing
│   └── requirements.txt
├── notebooks/                  # Operational playbooks for jobs
├── databricks/                 # Cluster + job definitions
├── docker/                     # Container build + compose for local parity
├── scripts/                    # Bootstrap and seeding utilities
├── README.md
└── .env.example
```

### Data model and Delta Lake strategy
| Table | Purpose | Schema highlights | Partitioning | Versioning |
| --- | --- | --- | --- | --- |
| `raw_documents` | Landing zone for uploaded files | id, name, source_path, ingestion_ts, content | `ingestion_date` for pruning | Delta time travel to audit uploads |
| `parsed_documents` | Cleaned/normalized text | inherits id + cleaned_text | `ingestion_date` | Tracks lineage to raw via delta history |
| `chunked_documents` | Overlapping spans | document_id, chunk_index, content | `document_id` for co-locating | Delta change data feed supports re-embedding |
| `embedded_chunks` | Vectorized chunks | chunk_id, embedding array | `document_id` | Versioned so vector indexes can sync to specific versions |

### Vector Search
- `backend/app/databricks/vector_search.py` abstracts Databricks Vector Search calls and logs creation via `ensure_vector_index()`. The mock implementation hashes text for deterministic local vectors while keeping the same contract for the managed service.
- Retrieval uses `search(query, k)` to return top-k chunks. Swap in the Databricks SDK client to call `VectorSearchClient.query` without altering higher layers.

### MLflow
- Every pipeline stage logs parameters and metrics: embedding model version, LLM, prompt version, and simple relevance/latency metrics. See `EmbeddingService` and `GenerationService` for logging paths.
- `mlflow_tracking.py` centralizes experiment setup to support both Databricks-hosted tracking URIs and local testing.

### Databricks Jobs
- Job JSONs in `databricks/job_definitions` show how ingestion, embedding, and evaluation can run on schedules (cron) or ad hoc triggers.
- The same notebooks are runnable locally for debugging before promotion to Jobs.

## End-to-end flow
1. **Ingest** – `/ingest` accepts PDF/text/markdown uploads, normalizes content, and writes to `raw_documents` Delta with partitioning by ingestion date. `scripts/seed_sample_data.py` demonstrates a code path without file I/O for CI.
2. **Process** – `ChunkingService` cleans and splits text with overlap, persisting chunks to `chunked_documents` (partitioned by `document_id`).
3. **Embed** – `EmbeddingService` logs embedding model versions to MLflow, writes embeddings to `embedded_chunks`, and upserts into Vector Search.
4. **Index** – `vector_search.ensure_vector_index()` establishes or syncs the index against the embedded Delta table. Local FAISS parity is simulated for offline dev.
5. **Retrieve** – `RetrievalService` queries Vector Search for top-k hits with scores to ground responses.
6. **Generate** – `GenerationService` builds RAG prompts from `prompts/rag_prompt.txt`, logs prompt versions, and calls the serving model endpoint (mocked here for portability).
7. **Evaluate** – `EvaluationService` records latency and heuristic relevance metrics into MLflow; hook in human feedback providers as needed.

## Running locally
1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r backend/requirements.txt`
3. `python scripts/bootstrap_local.py` to create MLflow experiment + mock tables/index.
4. `uvicorn app.main:app --reload --port 8000 --app-dir backend/app`
5. Optional: `python scripts/seed_sample_data.py` to preload content.

## Running on Databricks
1. Import notebooks under `/Workspace/notebooks` and attach them to the cluster defined in `databricks/cluster_config.json`.
2. Create a Unity Catalog schema matching `Settings.schema` and grant workspace principals.
3. Use `bootstrap_databricks.py` as a job or `%run` within a notebook to create tables and vector indexes.
4. Configure MLflow experiment paths (`Settings.experiment_name`) to log model/prompt/metric lineage.
5. Deploy FastAPI service via container image built from `docker/Dockerfile` to Model Serving or a compute cluster with port forwarding.

## How this differs from a basic RAG demo
- Emphasizes **Delta-first** lineage with raw→parsed→chunked→embedded tables, partitioning, and versioning considerations.
- Uses **Vector Search** instead of bespoke ANN, with local FAISS-like parity to keep dev velocity high.
- Wires **MLflow tracking** for every stage including prompt versions and operational metrics.
- Provides **Databricks Jobs** JSON for scheduled ingestion/embedding/evaluation, not just ad hoc scripts.
- Ships **FastAPI backend + Docker** for productionization, not only notebooks.

## Trade-offs and limitations
- Vector search and LLM calls are mocked to keep the repo self-contained; wire to Databricks services before production.
- Security (authN/Z) is stubbed; add PAT/AAD auth, Secrets scopes, and table ACLs for enterprise rollout.
- The chunker is whitespace-based for clarity; replace with tokenizer-aware splitter to match embedding model context windows.

## Future extensions
- **Governance:** integrate Unity Catalog lineage and row-level permissions for sensitive documents.
- **Monitoring:** add request/response observability with Lakehouse Monitoring and MLflow model metrics dashboards.
- **Evaluation:** integrate offline evaluators and human feedback collection with prompt versioning gates.
- **Access control:** enforce workspace and cluster policies, rotate tokens/creds, and wrap APIs with OAuth.

