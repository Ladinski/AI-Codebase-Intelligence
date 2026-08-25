from sentence_transformers import CrossEncoder


class RerankerService:
    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        if not results:
            return []

        pairs = [
            (
                query,
                (
                    f"{result['path']}\n"
                    f"{result['content']}"
                ),
            )
            for result in results
        ]

        scores = self.model.predict(pairs)

        reranked = []

        for result, score in zip(
            results,
            scores,
        ):
            item = result.copy()
            item["reranker_score"] = float(score)
            reranked.append(item)

        reranked.sort(
            key=lambda result: result["reranker_score"],
            reverse=True,
        )

        return reranked[:top_k]