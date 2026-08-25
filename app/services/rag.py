from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.cache import CacheService
from app.services.hybrid_search import HybridSearchService
from app.services.llm import LLMService


class RAGService:
    def __init__(self):
        self.search = HybridSearchService()
        self.llm = LLMService()
        self.cache = CacheService()

    def answer(
        self,
        db: Session,
        repository_id: int,
        query: str,
        top_k: int = 5,
    ) -> dict:
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty")

        cache_key = self.cache.build_rag_key(
            repository_id=repository_id,
            query=query,
            top_k=top_k,
        )

        cached = self.cache.get_json(cache_key)

        if cached is not None:
            cached["cache_hit"] = True
            return cached

        results = self.search.search(
            db=db,
            repository_id=repository_id,
            query=query,
            top_k=top_k,
        )

        if not results:
            raise ValueError(
                "No relevant code context found"
            )

        context_parts = []
        citations = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            citation = (
                f"[{index}] "
                f"{result['path']}:"
                f"{result['start_line']}-"
                f"{result['end_line']}"
            )

            citations.append(
                {
                    "id": index,
                    "chunk_id": result["chunk_id"],
                    "path": result["path"],
                    "start_line": result["start_line"],
                    "end_line": result["end_line"],
                }
            )

            context_parts.append(
                f"{citation}\n"
                f"{result['content']}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are an AI codebase assistant.

Answer the user's question using ONLY the provided code context.

Rules:
- Do not invent files, functions, classes, or behavior.
- If the context does not contain enough information, say so.
- Explain the code clearly and concisely.
- Cite claims using the provided citation numbers such as [1] or [2].
- Do not create citations that were not provided.

QUESTION:
{query}

CODE CONTEXT:
{context}

ANSWER:
""".strip()

        generation = self.llm.generate(prompt)

        response = {
            "answer": generation["answer"],
            "citations": citations,
            "retrieved_chunks": len(results),
            "prompt_tokens": generation["prompt_tokens"],
            "completion_tokens": generation["completion_tokens"],
            "estimated_cost_usd": 0.0,
            "cache_hit": False,
        }

        self.cache.set_json(
            key=cache_key,
            value=response,
            ttl_seconds=settings.rag_cache_ttl_seconds,
        )

        return response