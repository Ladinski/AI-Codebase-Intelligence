from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CodeSymbol(Base):
    __tablename__ = "code_symbols"

    id: Mapped[int] = mapped_column(primary_key=True)

    code_file_id: Mapped[int] = mapped_column(
        ForeignKey("code_files.id", ondelete="CASCADE"),
        index=True,
    )

    name: Mapped[str] = mapped_column(String(500))

    symbol_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    start_line: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    end_line: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    code_file = relationship(
        "CodeFile",
        back_populates="symbols",
    )