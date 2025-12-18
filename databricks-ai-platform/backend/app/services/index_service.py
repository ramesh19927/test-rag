"""
Index service handles chunking, embedding, and persistence.
For Databricks this would map to Delta tables and Vector Search. Locally we persist
JSONL files to demonstrate the contract.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

from app.config import Settings
from app.rag.chunker import chunk_text
from app.rag.embeddings import EmbeddingClient


class IndexService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedding_client = EmbeddingClient(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
            vector_dim=settings.vector_dim,
        )
        self.chunk_dir = Path(self.settings.data_root) / "chunks"
        self.chunk_dir.mkdir(parents=True, exist_ok=True)
        self.embed_path = Path(self.settings.data_root) / "embeddings.jsonl"

    def chunk_document(self, parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = parsed["text"]
        chunks = chunk_text(text, self.settings.max_chunk_size, self.settings.chunk_overlap)
        records = []
        for i, chunk in enumerate(chunks):
            records.append(
                {
                    "document_id": parsed["document_id"],
                    "chunk_id": f"{parsed['document_id']}_chunk_{i}",
                    "text": chunk,
                }
            )
        (self.chunk_dir / f"{parsed['document_id']}.json").write_text(json.dumps(records, indent=2))
        return records

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        vectors = self.embedding_client.embed([c["text"] for c in chunks])
        for record, vector in zip(chunks, vectors):
            record["embedding"] = vector
        return chunks

    def persist_embeddings(self, records: List[Dict[str, Any]]):
        # Append-only JSONL to simulate a Delta table; Databricks mapping documented in README.
        with open(self.embed_path, "a") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    def load_embeddings(self) -> List[Dict[str, Any]]:
        if not self.embed_path.exists():
            return []
        return [json.loads(line) for line in self.embed_path.read_text().splitlines() if line]

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        embeddings = self.load_embeddings()
        if not embeddings:
            return []
        query_vec = self.embedding_client.embed([query])[0]
        query_arr = np.array(query_vec)
        scored = []
        for record in embeddings:
            score = float(np.dot(query_arr, np.array(record["embedding"])))
            scored.append({**record, "score": score})
        return sorted(scored, key=lambda r: r["score"], reverse=True)[:top_k]
