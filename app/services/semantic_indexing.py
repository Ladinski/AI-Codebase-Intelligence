from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.models.code_file import CodeFile
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService


class SemanticIndexingService:
    def __init__(self):
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStoreService()

    def index_repository(
        self,
        db: Session,
        repository_id: int,
    ) -> int:
        rows = db.execute(
            select(
                CodeChunk,
                CodeFile,
            )
            .join(
                CodeFile,
                CodeChunk.code_file_id == CodeFile.id,
            )
            .where(
                CodeFile.repository_id == repository_id
            )
        ).all()

        if not rows:
            raise ValueError(
                "Repository has no chunks to index"
            )

        texts = [
            chunk.content
            for chunk, _ in rows
        ]

        embeddings = self.embeddings.embed_batch(
            texts
        )

        vectors = []

        for (
            (chunk, code_file),
            embedding,
        ) in zip(rows, embeddings):
            vectors.append(
                {
                    "id": f"chunk-{chunk.id}",
                    "values": embedding,
                    "metadata": {
                        "repository_id": repository_id,
                        "code_file_id": code_file.id,
                        "chunk_id": chunk.id,
                        "path": code_file.path,
                        "language": code_file.language or "",
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "content": chunk.content,
                    },
                }
            )

        self.vector_store.upsert_chunks(
            repository_id=repository_id,
            vectors=vectors,
        )

        return len(vectors)