import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.repository import Repository
from app.models.user import User
from app.schemas.rag import RAGRequest, RAGResponse
from app.services.rag import RAGService


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)

service = RAGService()


@router.post(
    "/ask",
    response_model=RAGResponse,
)
def ask_repository(
    data: RAGRequest,
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
        return service.answer(
            db=db,
            repository_id=data.repository_id,
            query=data.query,
            top_k=data.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable",
        )