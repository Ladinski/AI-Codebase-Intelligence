from pydantic import BaseModel


class IngestionRequest(BaseModel):
    repository_id: int
    path: str


class IngestionResponse(BaseModel):
    repository_id: int
    files_ingested: int