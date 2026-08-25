from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings


INDEX_DIMENSION = 384


class VectorStoreService:
    def __init__(self):
        self.pc = Pinecone(
            api_key=settings.pinecone_api_key
        )

        self.index_name = settings.pinecone_index_name

        self._ensure_index()

        self.index = self.pc.Index(
            self.index_name
        )

    def _ensure_index(self):
        existing_indexes = [
            index.name
            for index in self.pc.list_indexes()
        ]

        if self.index_name in existing_indexes:
            return

        self.pc.create_index(
            name=self.index_name,
            dimension=INDEX_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            ),
        )

    def upsert_chunks(
        self,
        repository_id: int,
        vectors: list[dict],
    ):
        namespace = f"repository-{repository_id}"

        self.index.upsert(
            vectors=vectors,
            namespace=namespace,
        )

    def search(
        self,
        repository_id: int,
        query_vector: list[float],
        top_k: int = 5,
    ):
        namespace = f"repository-{repository_id}"

        return self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
        )