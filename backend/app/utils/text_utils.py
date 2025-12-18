"""Text processing utilities used across the pipeline."""
import re
from typing import Iterable, List


WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Lowercase and normalize whitespace to stabilize downstream embeddings."""
    cleaned = text.replace("\u00a0", " ")
    cleaned = WHITESPACE_RE.sub(" ", cleaned)
    return cleaned.strip().lower()


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Chunk text with token overlap to preserve context across splits."""
    tokens = text.split(" ")
    chunks: List[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens))
        start = end - overlap
        if start < 0:
            start = 0
        if end == len(tokens):
            break
    return chunks


def format_prompt(question: str, contexts: Iterable[str]) -> str:
    """Build the RAG prompt by joining contexts with the base template."""
    context_block = "\n\n".join(contexts)
    return f"Context:\n{context_block}\n\nQuestion: {question}\nAnswer:"
