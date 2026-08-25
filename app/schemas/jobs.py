from pydantic import BaseModel


class RepositoryIndexJobRequest(BaseModel):
    repository_id: int
    path: str


class RepositoryIndexJobResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None