"""
Lightweight generation utilities. Uses OpenAI when a key is available, otherwise
returns templated responses to keep the system runnable offline.
"""
from typing import List, Dict

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency
    openai = None


class Generator:
    def __init__(self, model: str, api_key: str | None):
        self.model = model
        self.api_key = api_key
        if api_key and openai:
            openai.api_key = api_key

    def synthesize_answer(self, question: str, contexts: List[Dict[str, str]]) -> str:
        if self.api_key and openai:
            prompt = self._build_prompt(question, contexts)
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion["choices"][0]["message"]["content"]
        context_preview = " | ".join(c["text"][:120] for c in contexts)
        return f"[offline-mode] Answer to '{question}' grounded in: {context_preview}"

    def structured_output(self, instruction: str, contexts: List[Dict[str, str]]) -> str:
        if self.api_key and openai:
            prompt = self._build_prompt(instruction, contexts)
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion["choices"][0]["message"]["content"]
        bullets = "\n".join(f"- {c['text'][:140]}" for c in contexts)
        return f"[offline-mode] {instruction}\nContext:\n{bullets}"

    def _build_prompt(self, query: str, contexts: List[Dict[str, str]]) -> str:
        joined = "\n".join([f"[doc:{c['document_id']}] {c['text']}" for c in contexts])
        return f"Use the following context to answer or generate the requested output.\n{joined}\nQuery: {query}"
