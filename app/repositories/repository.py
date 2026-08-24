from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.repository import Repository


class RepositoryRepository:
    def create(
        self,
        db: Session,
        name: str,
        source_url: str | None,
        owner_id: int,
    ) -> Repository:
        repository = Repository(
            name=name,
            source_url=source_url,
            owner_id=owner_id,
        )

        db.add(repository)
        db.commit()
        db.refresh(repository)

        return repository

    def get_all_by_owner(
        self,
        db: Session,
        owner_id: int,
    ) -> list[Repository]:
        statement = select(Repository).where(
            Repository.owner_id == owner_id
        )

        return list(db.scalars(statement).all())