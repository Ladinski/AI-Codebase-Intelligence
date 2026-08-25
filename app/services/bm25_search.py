import re

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.models.code_file import CodeFile


class BM25SearchService:
    def _tokenize(self, text: str) -> list[str]:
        return re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*|\d+",
            text.lower(),
        )

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
                "Repository has no chunks to search"
            )

        documents = []

        for chunk, code_file in rows:
            searchable_text = (
                f"{code_file.path}\n"
                f"{code_file.language or ''}\n"
                f"{chunk.content}"
            )

            documents.append(
                self._tokenize(searchable_text)
            )

        bm25 = BM25Okapi(documents)

        query_tokens = self._tokenize(query)

        scores = bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:
            chunk, code_file = rows[index]

            results.append(
                {
                    "chunk_id": chunk.id,
                    "path": code_file.path,
                    "language": code_file.language,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "content": chunk.content,
                    "score": float(scores[index]),
                }
            )

        return results