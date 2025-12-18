"""
Utility helpers to register Delta tables with Databricks Vector Search.
This is a placeholder script documenting how to map the local JSONL workflow
into production-grade vector search.
"""
from databricks.vector_search.client import VectorSearchClient


def create_or_update_index(endpoint: str, index_name: str, table_name: str):
    client = VectorSearchClient()
    endpoint = client.get_endpoint(endpoint)
    try:
        index = endpoint.get_index(index_name)
        index.update(delta_table_name=table_name, primary_key="chunk_id", embedding_dimension=512)
    except Exception:
        endpoint.create_delta_sync_index(
            index_name=index_name,
            primary_key="chunk_id",
            delta_table_name=table_name,
            embedding_dimension=512,
        )


if __name__ == "__main__":
    create_or_update_index(
        endpoint="vs_endpoint",
        index_name="document_intel_index",
        table_name="embeddings",
    )
