# Databricks Deployment Notes

This folder holds artifacts that translate the local FastAPI + JSONL experience into Databricks-native primitives.

## Key steps
1. Provision Unity Catalog and a DBFS or UC volume for raw file storage.
2. Run `schemas.sql` in a Databricks SQL warehouse to create Delta tables.
3. Use `vector_index.py` to register the `embeddings` table with Vector Search for low-latency similarity lookups.
4. Deploy the backend as a Databricks model serving endpoint or on a compute cluster with MLflow for model/prompt tracking.
5. Point `MODE=databricks` in the `.env` file and configure the JDBC/UC connection strings for persistence.

## Notebooks
Add migration or batch-processing notebooks under `notebooks/` as needed. The repository favors code-based services; notebooks are used only for operational jobs (e.g., bulk ingestion) rather than serving.
