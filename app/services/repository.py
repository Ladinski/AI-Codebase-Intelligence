from sqlalchemy.orm import Session

from app.models.repository import Repository
from app.repositories.repository import RepositoryRepository
from app.schemas.repository import RepositoryCreate


class RepositoryService:
    def __init__(self):
        self.repository = RepositoryRepository()

    def create_repository(
        self,
        db: Session,
        data: RepositoryCreate,
        owner_id: int,
    ) -> Repository:
        name = data.name.strip()

        if not name:
            raise ValueError("Repository name cannot be empty")

        return self.repository.create(
            db=db,
            name=name,
            source_url=data.source_url,
            owner_id=owner_id,
        )

    def get_repositories(
        self,
        db: Session,
        owner_id: int,
    ) -> list[Repository]:
        return self.repository.get_all_by_owner(
            db=db,
            owner_id=owner_id,
        )