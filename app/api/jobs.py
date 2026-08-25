from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.celery_app import celery_app
from app.core.database import get_db
from app.models.repository import Repository
from app.models.user import User
from app.schemas.jobs import (
    JobStatusResponse,
    RepositoryIndexJobRequest,
    RepositoryIndexJobResponse,
)
from app.tasks.repository_indexing import (
    index_repository_task,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Background Jobs"],
)


@router.post(
    "/index-repository",
    response_model=RepositoryIndexJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_repository_indexing(
    data: RepositoryIndexJobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = db.get(
        Repository,
        data.repository_id,
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    if repository.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Repository does not belong to current user",
        )

    task = index_repository_task.delay(
        repository_id=data.repository_id,
        owner_id=current_user.id,
        path=data.path,
    )

    return RepositoryIndexJobResponse(
        job_id=task.id,
        status="queued",
    )


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
)
def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    task = celery_app.AsyncResult(job_id)

    result = None

    if task.successful():
        result = task.result

    elif task.state == "PROGRESS":
        result = task.info

    elif task.failed():
        result = {
            "error": str(task.result),
        }

    return JobStatusResponse(
        job_id=job_id,
        status=task.state,
        result=result,
    )