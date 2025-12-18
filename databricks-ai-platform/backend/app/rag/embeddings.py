"""
Embedding helpers. Defaults to a deterministic local embedding to avoid remote calls,
but can leverage OpenAI when an API key is provided. The design keeps the interface
pluggable so Databricks foundation models or Vector Search APIs can be dropped in.
"""
import hashlib
import numpy as np
from typing import List

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency
    openai = None


class EmbeddingClient:
    def __init__(self, model: str, api_key: str | None, vector_dim: int = 512):
        self.model = model
        self.api_key = api_key
        self.vector_dim = vector_dim
        if api_key and openai:
            openai.api_key = api_key

    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.api_key and openai:
            response = openai.Embedding.create(model=self.model, input=texts)
            return [item["embedding"] for item in response["data"]]
        return [self._local_embedding(t) for t in texts]

    def _local_embedding(self, text: str) -> List[float]:
        # Simple deterministic hashing-based embedding to avoid network requirements.
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.vector_dim)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0
