import json
from pathlib import Path

from app.core.database import SessionLocal
from app.services.bm25_search import BM25SearchService
from app.services.hybrid_search import HybridSearchService
from app.services.semantic_search import SemanticSearchService
from app.services.reranked_search import RerankedSearchService

REPOSITORY_ID = 2
TOP_K = 5

CASES_PATH = Path(
    "evaluation/retrieval_cases.json"
)


def hit_at_k(
    results: list[dict],
    relevant_paths: list[str],
) -> float:
    returned_paths = {
        result["path"]
        for result in results[:TOP_K]
    }

    return float(
        bool(returned_paths & set(relevant_paths))
    )


def reciprocal_rank(
    results: list[dict],
    relevant_paths: list[str],
) -> float:
    relevant = set(relevant_paths)

    for rank, result in enumerate(
        results[:TOP_K],
        start=1,
    ):
        if result["path"] in relevant:
            return 1.0 / rank

    return 0.0


def main():
    with CASES_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    db = SessionLocal()

    bm25 = BM25SearchService()
    semantic = SemanticSearchService()
    hybrid = HybridSearchService()
    reranked = RerankedSearchService()

    scores = {
        "bm25": {
            "hit": [],
            "rr": [],
        },
        "semantic": {
            "hit": [],
            "rr": [],
        },
        "hybrid": {
            "hit": [],
            "rr": [],
        },
        "reranked": {
            "hit": [],
            "rr": [],
        },
    }

    try:
        for case in cases:
            query = case["query"]
            relevant = case["relevant_paths"]

            bm25_results = bm25.search(
                db=db,
                repository_id=REPOSITORY_ID,
                query=query,
                top_k=TOP_K,
            )

            semantic_results = semantic.search(
                repository_id=REPOSITORY_ID,
                query=query,
                top_k=TOP_K,
            )

            hybrid_results = hybrid.search(
                db=db,
                repository_id=REPOSITORY_ID,
                query=query,
                top_k=TOP_K,
            )

            reranked_results = reranked.search(
                db=db,
                repository_id=REPOSITORY_ID,
                query=query,
                top_k=TOP_K,
            )

            methods = {
                "bm25": bm25_results,
                "semantic": semantic_results,
                "hybrid": hybrid_results,
                "reranked": reranked_results,
            }

            print(f"\nQUERY: {query}")

            for name, results in methods.items():
                hit = hit_at_k(
                    results,
                    relevant,
                )

                rr = reciprocal_rank(
                    results,
                    relevant,
                )

                scores[name]["hit"].append(hit)
                scores[name]["rr"].append(rr)

                print(
                    f"{name:10} "
                    f"Hit@{TOP_K}={hit:.0f} "
                    f"RR={rr:.3f}"
                )

        print("\n=== RETRIEVAL EVALUATION ===")

        for name, values in scores.items():
            hit_rate = (
                sum(values["hit"])
                / len(values["hit"])
            )

            mrr = (
                sum(values["rr"])
                / len(values["rr"])
            )

            print(
                f"{name:10} "
                f"Hit@{TOP_K}={hit_rate:.3f} "
                f"MRR@{TOP_K}={mrr:.3f}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()