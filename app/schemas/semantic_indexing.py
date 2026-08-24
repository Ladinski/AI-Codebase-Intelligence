from pydantic import BaseModel


class SemanticIndexRequest(BaseModel):
    repository_id: int


class SemanticIndexResponse(BaseModel):
    repository_id: int
    vectors_indexed: int