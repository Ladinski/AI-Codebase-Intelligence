from sqlalchemy import select

from mcp.server import MCPServer

from app.core.database import SessionLocal
from app.models.code_file import CodeFile
from app.models.code_symbol import CodeSymbol
from app.services.hybrid_search import HybridSearchService
from app.services.rag import RAGService


mcp = MCPServer("AI Codebase Intelligence")

search_service = HybridSearchService()
rag_service = RAGService()


@mcp.tool()
def search_code(
    repository_id: int,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Search a repository using hybrid semantic and BM25 retrieval."""

    db = SessionLocal()

    try:
        return search_service.search(
            db=db,
            repository_id=repository_id,
            query=query,
            top_k=top_k,
        )
    finally:
        db.close()


@mcp.tool()
def get_file(
    repository_id: int,
    path: str,
) -> dict:
    """Read one indexed source file from a repository."""

    db = SessionLocal()

    try:
        file = db.scalar(
            select(CodeFile).where(
                CodeFile.repository_id == repository_id,
                CodeFile.path == path,
            )
        )

        if file is None:
            return {
                "found": False,
                "error": "File not found",
            }

        return {
            "found": True,
            "path": file.path,
            "language": file.language,
            "content": file.content,
        }

    finally:
        db.close()


@mcp.tool()
def list_symbols(
    repository_id: int,
    limit: int = 50,
) -> list[dict]:
    """List structured code symbols extracted from a repository."""

    db = SessionLocal()

    try:
        rows = db.execute(
            select(
                CodeSymbol,
                CodeFile,
            )
            .join(
                CodeFile,
                CodeSymbol.code_file_id == CodeFile.id,
            )
            .where(
                CodeFile.repository_id == repository_id
            )
            .limit(limit)
        ).all()

        return [
            {
                "name": symbol.name,
                "type": symbol.symbol_type,
                "path": code_file.path,
                "start_line": symbol.start_line,
                "end_line": symbol.end_line,
            }
            for symbol, code_file in rows
        ]

    finally:
        db.close()


@mcp.tool()
def ask_codebase(
    repository_id: int,
    query: str,
) -> dict:
    """Ask a grounded question about an indexed repository."""

    db = SessionLocal()

    try:
        return rag_service.answer(
            db=db,
            repository_id=repository_id,
            query=query,
            top_k=5,
        )

    finally:
        db.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")