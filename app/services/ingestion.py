from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.code_file import CodeFile
from app.models.repository import Repository


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cs",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".html",
    ".css",
    ".sql",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "migrations",
    "evaluation",
}

IGNORED_FILES = {
    "README.md",
}

MAX_FILE_SIZE = 1_000_000


class IngestionService:
    def ingest_repository(
        self,
        db: Session,
        repository_id: int,
        owner_id: int,
        path: str,
    ) -> int:
        repository = db.get(Repository, repository_id)

        if repository is None:
            raise ValueError("Repository not found")

        if repository.owner_id != owner_id:
            raise PermissionError(
                "Repository does not belong to current user"
            )

        root = Path(path)

        if not root.exists():
            raise ValueError("Path does not exist")

        if not root.is_dir():
            raise ValueError("Path must be a directory")

        db.execute(
            delete(CodeFile).where(
                CodeFile.repository_id == repository_id
            )
        )

        files_ingested = 0

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue

            relative_path = file_path.relative_to(root)

            if any(
                part in IGNORED_DIRECTORIES
                for part in relative_path.parts
            ):
                continue

            if relative_path.name in IGNORED_FILES:
                continue

            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                content = file_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

            except OSError:
                continue

            code_file = CodeFile(
                path=str(relative_path),
                language=file_path.suffix.lower().lstrip("."),
                content=content,
                repository_id=repository_id,
            )

            db.add(code_file)
            files_ingested += 1

        db.commit()

        return files_ingested