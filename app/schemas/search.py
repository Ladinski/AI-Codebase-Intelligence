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


class BM25SearchRequest(BaseModel):
    repository_id: int
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class BM25SearchResult(BaseModel):
    chunk_id: int
    path: str
    language: str | None
    start_line: int
    end_line: int
    content: str
    score: float


class BM25SearchResponse(BaseModel):
    query: str
    results: list[BM25SearchResult]


class HybridSearchRequest(BaseModel):
    repository_id: int
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class HybridSearchResult(BaseModel):
    chunk_id: int
    path: str
    language: str | None
    start_line: int
    end_line: int
    content: str
    rrf_score: float

    semantic_rank: int | None
    bm25_rank: int | None

    semantic_score: float | None
    bm25_score: float | None


class HybridSearchResponse(BaseModel):
    query: str
    results: list[HybridSearchResult]