from sqlalchemy.orm import Session

from app.services.hybrid_search import HybridSearchService
from app.services.reranker import RerankerService


class RerankedSearchService:
    def __init__(self):
        self.hybrid = HybridSearchService()
        self.reranker = RerankerService()

    def search(
        self,
        db: Session,
        repository_id: int,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty")

        candidate_count = max(
            top_k * 4,
            20,
        )

        candidates = self.hybrid.search(
            db=db,
            repository_id=repository_id,
            query=query,
            top_k=candidate_count,
        )

        return self.reranker.rerank(
            query=query,
            results=candidates,
            top_k=top_k,
        )