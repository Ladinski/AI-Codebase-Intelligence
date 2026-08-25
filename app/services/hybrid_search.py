from sqlalchemy.orm import Session

from app.services.bm25_search import BM25SearchService
from app.services.semantic_search import SemanticSearchService


RRF_K = 60


class HybridSearchService:
    def __init__(self):
        self.semantic = SemanticSearchService()
        self.bm25 = BM25SearchService()

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

        candidate_count = max(top_k * 4, 20)

        semantic_results = self.semantic.search(
            repository_id=repository_id,
            query=query,
            top_k=candidate_count,
        )

        bm25_results = self.bm25.search(
            db=db,
            repository_id=repository_id,
            query=query,
            top_k=candidate_count,
        )

        fused: dict[int, dict] = {}

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            chunk_id = result["chunk_id"]

            if chunk_id is None:
                continue

            fused[chunk_id] = {
                **result,
                "rrf_score": 0.0,
                "semantic_rank": rank,
                "bm25_rank": None,
                "semantic_score": result["score"],
                "bm25_score": None,
            }

            fused[chunk_id]["rrf_score"] += (
                1 / (RRF_K + rank)
            )

        for rank, result in enumerate(
            bm25_results,
            start=1,
        ):
            chunk_id = result["chunk_id"]

            if chunk_id not in fused:
                fused[chunk_id] = {
                    **result,
                    "rrf_score": 0.0,
                    "semantic_rank": None,
                    "bm25_rank": rank,
                    "semantic_score": None,
                    "bm25_score": result["score"],
                }
            else:
                fused[chunk_id]["bm25_rank"] = rank
                fused[chunk_id]["bm25_score"] = result["score"]

            fused[chunk_id]["rrf_score"] += (
                1 / (RRF_K + rank)
            )

        ranked_results = sorted(
            fused.values(),
            key=lambda result: result["rrf_score"],
            reverse=True,
        )

        return ranked_results[:top_k]