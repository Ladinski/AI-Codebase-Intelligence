from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.repository import Repository
from app.models.user import User
from app.schemas.metadata import (
    MetadataExtractionRequest,
    MetadataExtractionResponse,
)
from app.services.metadata_extraction import (
    MetadataExtractionService,
)


router = APIRouter(
    prefix="/metadata",
    tags=["Metadata"],
)

service = MetadataExtractionService()


@router.post(
    "/extract",
    response_model=MetadataExtractionResponse,
)
def extract_metadata(
    data: MetadataExtractionRequest,
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

    try:
        count = service.extract_repository(
            db=db,
            repository_id=data.repository_id,
        )

        return MetadataExtractionResponse(
            repository_id=data.repository_id,
            symbols_created=count,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )