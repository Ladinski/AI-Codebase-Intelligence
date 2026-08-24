import ast

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.code_file import CodeFile
from app.models.code_symbol import CodeSymbol


class MetadataExtractionService:
    def extract_repository(
        self,
        db: Session,
        repository_id: int,
    ) -> int:
        files = db.scalars(
            select(CodeFile).where(
                CodeFile.repository_id == repository_id
            )
        ).all()

        if not files:
            raise ValueError("Repository has no ingested files")

        file_ids = [file.id for file in files]

        db.execute(
            delete(CodeSymbol).where(
                CodeSymbol.code_file_id.in_(file_ids)
            )
        )

        symbols_created = 0

        for code_file in files:
            if code_file.language != "py":
                continue

            symbols = self._extract_python_symbols(
                code_file.content
            )

            for symbol in symbols:
                db.add(
                    CodeSymbol(
                        code_file_id=code_file.id,
                        name=symbol["name"],
                        symbol_type=symbol["symbol_type"],
                        start_line=symbol["start_line"],
                        end_line=symbol["end_line"],
                    )
                )

                symbols_created += 1

        db.commit()

        return symbols_created

    def _extract_python_symbols(
        self,
        content: str,
    ) -> list[dict]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    {
                        "name": node.name,
                        "symbol_type": "class",
                        "start_line": node.lineno,
                        "end_line": getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        ),
                    }
                )

            elif isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                symbols.append(
                    {
                        "name": node.name,
                        "symbol_type": (
                            "async_function"
                            if isinstance(
                                node,
                                ast.AsyncFunctionDef,
                            )
                            else "function"
                        ),
                        "start_line": node.lineno,
                        "end_line": getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        ),
                    }
                )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    symbols.append(
                        {
                            "name": alias.name,
                            "symbol_type": "import",
                            "start_line": node.lineno,
                            "end_line": node.lineno,
                        }
                    )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                for alias in node.names:
                    name = (
                        f"{module}.{alias.name}"
                        if module
                        else alias.name
                    )

                    symbols.append(
                        {
                            "name": name,
                            "symbol_type": "import",
                            "start_line": node.lineno,
                            "end_line": node.lineno,
                        }
                    )

        return symbols