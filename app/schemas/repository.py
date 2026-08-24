from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryCreate(BaseModel):
    name: str
    source_url: str | None = None


class RepositoryResponse(BaseModel):
    id: int
    name: str
    source_url: str | None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)