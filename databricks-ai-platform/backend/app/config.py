"""
Configuration management for the application.
Supports local and Databricks modes via environment variables.
"""
from functools import lru_cache
from pydantic import BaseSettings, Field
from typing import Literal


class Settings(BaseSettings):
    app_name: str = Field("databricks-ai-platform", description="Application name")
    mode: Literal["local", "databricks"] = Field(
        "local", description="Execution mode: local filesystem or Databricks services"
    )
    data_root: str = Field(
        "./.data", description="Root path for local file persistence when in local mode"
    )
    database_url: str = Field(
        "sqlite:///./.data/rag.db",
        description="SQLAlchemy database URL; in Databricks mode point to Hive or UC",
    )
    openai_api_key: str | None = Field(
        default=None, description="Optional OpenAI API key for embedding and generation"
    )
    embedding_model: str = Field(
        "text-embedding-3-small",
        description="Default embedding model; pluggable for Databricks foundation models",
    )
    max_chunk_size: int = Field(800, description="Max characters per text chunk")
    chunk_overlap: int = Field(150, description="Overlap between chunks for context")
    vector_dim: int = Field(512, description="Dimension for lightweight local embeddings")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
