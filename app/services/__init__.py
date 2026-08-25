from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.cache import CacheService
from app.services.hybrid_search import HybridSearchService
from app.services.llm import LLMService
from app.services.reranked_search import RerankedSearchService

class RAGService:
    def __init__(self):
        self.search = HybridSearchService()
        self.llm = LLMService()
        self.cache = CacheService()
        self.search = RerankedSearchService()

    def answer(
        self,
        db: Session,
        repository_id: int,
        query: str,
        top_k: int = 5,
    ) -> dict:
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty")