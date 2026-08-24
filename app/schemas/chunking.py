from pydantic import BaseModel


class ChunkRepositoryRequest(BaseModel):
    repository_id: int


class ChunkRepositoryResponse(BaseModel):
    repository_id: int
    chunks_created: int