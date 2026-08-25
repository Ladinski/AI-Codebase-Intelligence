from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    repository_id: int
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class SemanticSearchResult(BaseModel):
    chunk_id: int | None
    path: str | None
    language: str | None
    start_line: int | None
    end_line: int | None
    content: str | None
    score: float


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchResult]