from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.ingestion import router as ingestion_router
from app.api.repositories import router as repositories_router
from app.api.chunking import router as chunking_router
from app.api.metadata import router as metadata_router
from app.api.semantic_indexing import (
    router as semantic_indexing_router,
)

app = FastAPI(
    title="AI Codebase Intelligence API",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(repositories_router)
app.include_router(ingestion_router)
app.include_router(chunking_router)
app.include_router(metadata_router)
app.include_router(semantic_indexing_router)

@app.get("/health")
def health():
    return {"status": "ok"}