"""RAG pipeline orchestrating search and generation."""
from typing import List, Tuple

from app.config import Settings
from app.services.index_service import IndexService
from app.rag.generator import Generator


class RagPipeline:
    def __init__(self, settings: Settings, index_service: IndexService):
        self.index_service = index_service
        self.generator = Generator(model="gpt-4o-mini", api_key=settings.openai_api_key)

    def answer_question(self, question: str, top_k: int = 4) -> Tuple[str, List[dict]]:
        contexts = self.index_service.search(question, top_k=top_k)
        answer = self.generator.synthesize_answer(question, contexts)
        return answer, contexts

    def generate_structured(self, instruction: str, top_k: int = 4) -> Tuple[str, List[dict]]:
        contexts = self.index_service.search(instruction, top_k=top_k)
        output = self.generator.structured_output(instruction, contexts)
        return output, contexts
