from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CodeFile(Base):
    __tablename__ = "code_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(1000))
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    repository = relationship(
        "Repository",
        back_populates="files",
    )

    chunks = relationship(
    "CodeChunk",
    back_populates="code_file",
    cascade="all, delete-orphan",
)

    symbols = relationship(
    "CodeSymbol",
    back_populates="code_file",
    cascade="all, delete-orphan",
)