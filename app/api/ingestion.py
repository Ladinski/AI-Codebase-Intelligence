from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.ingestion import (
    IngestionRequest,
    IngestionResponse,
)
from app.services.ingestion import IngestionService


router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)

service = IngestionService()


@router.post(
    "",
    response_model=IngestionResponse,
    status_code=status.HTTP_200_OK,
)
def ingest_repository(
    data: IngestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        count = service.ingest_repository(
            db=db,
            repository_id=data.repository_id,
            owner_id=current_user.id,
            path=data.path,
        )

        return IngestionResponse(
            repository_id=data.repository_id,
            files_ingested=count,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )