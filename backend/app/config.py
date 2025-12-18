"""Central configuration for the platform."""
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Environment-driven settings shared across services."""

    databricks_host: str = Field("http://localhost:18080", description="Databricks workspace host")
    databricks_token: str = Field("dapi-PLACEHOLDER", description="Personal access token or AAD token")
    catalog: str = Field("main", description="Unity Catalog name for storage")
    schema: str = Field("rag_platform", description="Schema used for Delta tables")
    vector_index_name: str = Field("rag_chunks_vs", description="Vector Search index name")
    embedding_model: str = Field("databricks-bge-large-en", description="Default embedding model")
    llm_model: str = Field("databricks-dbrx-instruct", description="Default LLM for generation")
    experiment_name: str = Field("/Shared/rag-platform", description="MLflow experiment name")
    chunk_size: int = Field(800, description="Chunk size for text splitting")
    chunk_overlap: int = Field(120, description="Token overlap between chunks")
    log_level: str = Field("INFO", description="Logging verbosity")
    local_vector_store_path: str = Field("/tmp/vector_store.faiss", description="Local FAISS file for parity")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance to avoid re-parsing environment."""
    return Settings()
