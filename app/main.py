from fastapi import FastAPI

from app.api.repositories import router as repositories_router


app = FastAPI(
    title="AI Codebase Intelligence API",
    version="0.1.0",
)

app.include_router(repositories_router)


@app.get("/health")
def health():
    return {"status": "ok"}