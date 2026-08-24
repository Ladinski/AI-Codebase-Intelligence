from pydantic import BaseModel


class MetadataExtractionRequest(BaseModel):
    repository_id: int


class MetadataExtractionResponse(BaseModel):
    repository_id: int
    symbols_created: int