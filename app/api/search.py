from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.repository import Repository
from app.models.user import User
from app.services.reranked_search import RerankedSearchService
from app.services.bm25_search import BM25SearchService
from app.services.hybrid_search import HybridSearchService
from app.schemas.search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    BM25SearchRequest,
    BM25SearchResponse,
    HybridSearchRequest,
    HybridSearchResponse,
    RerankedSearchRequest,
    RerankedSearchResponse,
)
from app.services.semantic_search import SemanticSearchService


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

service = SemanticSearchService()
bm25_service = BM25SearchService()
hybrid_service = HybridSearchService()
reranked_service = RerankedSearchService()

@router.post(
    "/semantic",
    response_model=SemanticSearchResponse,
)
def semantic_search(
    data: SemanticSearchRequest,
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
        results = service.search(
            repository_id=data.repository_id,
            query=data.query,
            top_k=data.top_k,
        )

        return SemanticSearchResponse(
            query=data.query,
            results=results,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/bm25",
    response_model=BM25SearchResponse,
)
def bm25_search(
    data: BM25SearchRequest,
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
        results = bm25_service.search(
            db=db,
            repository_id=data.repository_id,
            query=data.query,
            top_k=data.top_k,
        )

        return BM25SearchResponse(
            query=data.query,
            results=results,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/hybrid",
    response_model=HybridSearchResponse,
)
def hybrid_search(
    data: HybridSearchRequest,
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
        results = hybrid_service.search(
            db=db,
            repository_id=data.repository_id,
            query=data.query,
            top_k=data.top_k,
        )

        return HybridSearchResponse(
            query=data.query,
            results=results,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post(
    "/reranked",
    response_model=RerankedSearchResponse,
)
def reranked_search(
    data: RerankedSearchRequest,
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
        results = reranked_service.search(
            db=db,
            repository_id=data.repository_id,
            query=data.query,
            top_k=data.top_k,
        )

        return RerankedSearchResponse(
            query=data.query,
            results=results,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )   