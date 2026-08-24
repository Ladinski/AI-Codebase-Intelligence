from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.models.code_file import CodeFile


CHUNK_SIZE = 80
CHUNK_OVERLAP = 15


class ChunkingService:
    def chunk_repository(
        self,
        db: Session,
        repository_id: int,
    ) -> int:
        files = db.scalars(
            select(CodeFile).where(
                CodeFile.repository_id == repository_id
            )
        ).all()

        if not files:
            raise ValueError("Repository has no ingested files")

        file_ids = [file.id for file in files]

        db.execute(
            delete(CodeChunk).where(
                CodeChunk.code_file_id.in_(file_ids)
            )
        )

        chunks_created = 0

        for code_file in files:
            lines = code_file.content.splitlines()

            if not lines:
                continue

            start = 0
            chunk_index = 0

            while start < len(lines):
                end = min(
                    start + CHUNK_SIZE,
                    len(lines),
                )

                chunk_lines = lines[start:end]

                content = "\n".join(chunk_lines).strip()

                if content:
                    chunk = CodeChunk(
                        code_file_id=code_file.id,
                        chunk_index=chunk_index,
                        start_line=start + 1,
                        end_line=end,
                        content=content,
                    )

                    db.add(chunk)

                    chunks_created += 1
                    chunk_index += 1

                if end == len(lines):
                    break

                start = end - CHUNK_OVERLAP

        db.commit()

        return chunks_created