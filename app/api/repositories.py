from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
)
from app.services.repository import RepositoryService


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)

service = RepositoryService()

TEMP_USER_ID = 1


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repository(
    data: RepositoryCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_repository(
            db=db,
            data=data,
            owner_id=TEMP_USER_ID,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[RepositoryResponse],
)
def get_repositories(
    db: Session = Depends(get_db),
):
    return service.get_repositories(
        db=db,
        owner_id=TEMP_USER_ID,
    )