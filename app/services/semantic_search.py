from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService


class SemanticSearchService:
    def __init__(self):
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStoreService()

    def search(
        self,
        repository_id: int,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty")

        query_vector = self.embeddings.embed_text(query)

        response = self.vector_store.search(
            repository_id=repository_id,
            query_vector=query_vector,
            top_k=top_k,
        )

        results = []

        for match in response.matches:
            metadata = match.metadata or {}

            results.append(
                {
                    "chunk_id": metadata.get("chunk_id"),
                    "path": metadata.get("path"),
                    "language": metadata.get("language"),
                    "start_line": metadata.get("start_line"),
                    "end_line": metadata.get("end_line"),
                    "content": metadata.get("content"),
                    "score": match.score,
                }
            )

        return results