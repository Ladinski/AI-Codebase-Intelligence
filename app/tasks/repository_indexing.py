from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.chunking import ChunkingService
from app.services.ingestion import IngestionService
from app.services.metadata_extraction import MetadataExtractionService
from app.services.semantic_indexing import SemanticIndexingService


@celery_app.task(
    bind=True,
    name="index_repository",
)
def index_repository_task(
    self,
    repository_id: int,
    owner_id: int,
    path: str,
):
    db = SessionLocal()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"stage": "ingestion"},
        )

        files_ingested = IngestionService().ingest_repository(
            db=db,
            repository_id=repository_id,
            owner_id=owner_id,
            path=path,
        )

        self.update_state(
            state="PROGRESS",
            meta={"stage": "chunking"},
        )

        chunks_created = ChunkingService().chunk_repository(
            db=db,
            repository_id=repository_id,
        )

        self.update_state(
            state="PROGRESS",
            meta={"stage": "metadata"},
        )

        symbols_created = (
            MetadataExtractionService().extract_repository(
                db=db,
                repository_id=repository_id,
            )
        )

        self.update_state(
            state="PROGRESS",
            meta={"stage": "semantic_indexing"},
        )

        vectors_indexed = (
            SemanticIndexingService().index_repository(
                db=db,
                repository_id=repository_id,
            )
        )

        return {
            "repository_id": repository_id,
            "files_ingested": files_ingested,
            "chunks_created": chunks_created,
            "symbols_created": symbols_created,
            "vectors_indexed": vectors_indexed,
        }

    finally:
        db.close()