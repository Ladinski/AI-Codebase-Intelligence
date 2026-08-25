from pydantic import BaseModel, Field


class RAGRequest(BaseModel):
    repository_id: int
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class Citation(BaseModel):
    id: int
    chunk_id: int
    path: str
    start_line: int
    end_line: int


class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_chunks: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float